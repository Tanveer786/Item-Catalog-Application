#!/usr/bin/env python
"""
Item Catalog is a web application built using Flask Framework.

This application provides a list of items within a variety of categories and
integrated third-party authentication. Authenticated users have the ability to
post, edit and delete their own items.
"""

import random
import string
import httplib2
import json
import requests
from sqlalchemy import create_engine, asc
from sqlalchemy.orm import sessionmaker
from database_setup import Base, Category, Item, User
from flask import Flask, render_template, request, redirect, jsonify, url_for
from flask import flash, make_response, session as login_session
from oauth2client.client import flow_from_clientsecrets, FlowExchangeError


app = Flask(__name__)

# Get client secrets from the json file
CLIENT_ID = json.loads(
    open('client_secrets.json', 'r').read())['web']['client_id']
APPLICATION_NAME = "Item Catalog Application"


# Connect to Database and create database session
engine = create_engine('sqlite:///itemcatalog.db',
                       connect_args={'check_same_thread': False})
Base.metadata.bind = engine
DBSession = sessionmaker(bind=engine)
session = DBSession()


# User Helper Functions
def createUser(login_session):
    """
    createUser adds the new user to the database and returns the user id.

    createUser creates the user object using the info from input parameter
    login_session, adds it to database and returns the ID of the created user.

    args:
    login_session - flask session object.

    returns:
    ID of User added to the database.
    """
    newUser = User(name=login_session['username'], email=login_session[
                   'email'], picture=login_session['picture'])
    session.add(newUser)
    session.commit()
    user = session.query(User).filter_by(email=login_session['email']).one()
    return user.id


def getUserID(email):
    """
    getUserID returns the User ID.

    getUserID takes email as parameter and returns the ID of User associated
    with the email.

    args:
    email - email address of the user.

    returns:
    ID of user associated with given email address.
    """
    user = session.query(User).filter_by(email=email).first()
    if not user:
        return None
    return user.id


# Create anti-forgery state token
@app.route('/catalog/login')
def showLogin():
    """
    showLogin renders the login.html template.

    showLogin generates an anti-forgery state token which is a randomly chosen
    32 character string of digits and uppercase letters. Further login.html
    template is rendered by passing state token as parameter.

    returns:
    login.html template.
    """
    state = ''.join(random.choice(string.ascii_uppercase + string.digits)
                    for x in xrange(32))
    login_session['state'] = state
    # return "The current session state is %s" % login_session['state']
    return render_template('login.html', STATE=state)


@app.route('/gconnect', methods=['POST'])
def gconnect():
    """
    gconnect logs in the user to application.

    gconnect validates the state token, gets authorization code, upgrades the
    code into a credentials object, checks if access token is valid, verifies if
    access token is for intended user(and this app), stores the user info into a
    login_session object and returns a login successful message.

    return:
    successful login message.
    """
    # Validate state token
    if request.args.get('state') != login_session['state']:
        response = make_response(json.dumps('Invalid state parameter.'), 401)
        response.headers['Content-Type'] = 'application/json'
        return response
    # Obtain authorization code
    code = request.data

    try:
        # Upgrade the authorization code into a credentials object
        oauth_flow = flow_from_clientsecrets('client_secrets.json', scope='')
        oauth_flow.redirect_uri = 'postmessage'
        credentials = oauth_flow.step2_exchange(code)
    except FlowExchangeError:
        response = make_response(
            json.dumps('Failed to upgrade the authorization code.'), 401)
        response.headers['Content-Type'] = 'application/json'
        return response

    # Check that the access token is valid.
    access_token = credentials.access_token
    url = ('https://www.googleapis.com/oauth2/v1/tokeninfo?access_token=%s'
           % access_token)
    h = httplib2.Http()
    result = json.loads(h.request(url, 'GET')[1])

    # If there was an error in the access token info, abort.
    if result.get('error') is not None:
        response = make_response(json.dumps(result.get('error')), 500)
        response.headers['Content-Type'] = 'application/json'
        return response

    # Verify that the access token is used for the intended user.
    gplus_id = credentials.id_token['sub']
    if result['user_id'] != gplus_id:
        response = make_response(
            json.dumps("Token's user ID doesn't match given user ID."), 401)
        response.headers['Content-Type'] = 'application/json'
        return response

    # Verify that the access token is valid for this app.
    if result['issued_to'] != CLIENT_ID:
        response = make_response(
            json.dumps("Token's client ID does not match app's."), 401)
        print "Token's client ID does not match app's."
        response.headers['Content-Type'] = 'application/json'
        return response

    stored_access_token = login_session.get('access_token')
    stored_gplus_id = login_session.get('gplus_id')
    if stored_access_token is not None and gplus_id == stored_gplus_id:
        response = make_response(json.dumps('Current user is already    \
                                 connected.'), 200)
        response.headers['Content-Type'] = 'application/json'
        return response

    # Store the access token in the session for later use.
    login_session['access_token'] = credentials.access_token
    login_session['gplus_id'] = gplus_id

    # Get user info
    userinfo_url = "https://www.googleapis.com/oauth2/v1/userinfo"
    params = {'access_token': credentials.access_token, 'alt': 'json'}
    answer = requests.get(userinfo_url, params=params)

    data = answer.json()

    login_session['username'] = data['name']
    login_session['picture'] = data['picture']
    login_session['email'] = data['email']

    # See if a user exists, if it doesn't make a new one
    user_id = getUserID(data["email"])
    if not user_id:
        user_id = createUser(login_session)
    login_session['user_id'] = user_id

    output = ''
    output += '<h3>Welcome, '
    output += login_session['username']
    output += '!</h3>'
    output += '<img src="'
    output += login_session['picture']
    output += ''' " style = "width: 5em;
                             height: 5em;
                             border-radius: 3em;
                             -webkit-border-radius: 3em;
                             -moz-border-radius: 3em;"> '''

    flash("you are now logged in as %s" % login_session['username'])
    return output


# DISCONNECT - Revoke a current user's token and reset their login_session
@app.route('/gdisconnect')
def gdisconnect():
    """
    gdisconnect logs out the user from application.

    gdisconnect checks if user is connected, then sends the request to google
    oauth server asking to revoke the user's access token. If it's successful,
    user session info is deleted and redirected to home page.

    return:
    redirects to home page.
    """
    # Only disconnect a connected user.
    access_token = login_session.get('access_token')
    if access_token is None:
        response = make_response(
            json.dumps('Current user not connected.'), 401)
        response.headers['Content-Type'] = 'application/json'
        return response
    print ('In gdisconnect access token is %s', access_token)
    print ('User name is: ')
    print (login_session['username'])
    url = 'https://accounts.google.com/o/oauth2/revoke?token=%s' % access_token
    h = httplib2.Http()
    result = h.request(url, 'GET')[0]
    print ('result is ')
    print (result)

    if result['status'] == '200':
        # Reset the user's sesson.
        del login_session['access_token']
        del login_session['gplus_id']
        del login_session['username']
        del login_session['email']
        del login_session['picture']
        del login_session['user_id']

        flash('You were successfully logged out.')

        return redirect(url_for('catalogHome'))
    else:
        # For whatever reason, the given token was invalid.
        response = make_response(
            json.dumps('Failed to revoke token for given user.', 400))
        response.headers['Content-Type'] = 'application/json'
        return response


@app.route('/')
@app.route('/catalog/')
def catalogHome():
    """
    catalogHome renders the cataloghome.html template.

    catalogHome obtains the list of categories, latestItems added from database.
    It then renders cataloghome.html template by passing the parameters
    categories, latestItems and session object.

    returns:
    cataloghome.html template
    """
    categories = session.query(Category).all()
    latestItems = session.query(Item).order_by(
        Item.creation_date.desc()).limit(10).all()
    return render_template('cataloghome.html', categories=categories,
                           latestItems=latestItems, session=login_session)

@app.route('/catalog/about')
def aboutApplication():
    """
    aboutApplication renders about.html which describes about the application.
    """
    return render_template('about.html')


@app.route('/catalog/category/<int:category_id>/items')
def showItems(category_id):
    """
    showItem renders showitems.html which displays items in a category.

    showItems obtains categories, category associated with category_id and items
    in that category from database. It then renders showitems.html template by
    passing the obtained parameters.

    args:
    category_id - ID of a Category

    returns:
    showItems.html template which displays list of items in a selected category.
    """
    categories = session.query(Category).all()
    category = session.query(Category).filter_by(id=category_id).one()
    items = session.query(Item).filter_by(category_id=category_id).all()
    return render_template('showitems.html', categories=categories,
                           category=category, items=items)


@app.route('/catalog/category/<int:category_id>/item/<int:item_id>')
def viewItem(category_id, item_id):
    """
    viewItem displays item information.

    viewItem obtains item object associated with item_id from the database. It
    then renders the viewitem.html template by passing item and login_session
    objects as parameters.

    args:
    category_id - ID of a category
    item_id - ID of an item

    returns:
    viewitem.html template which displays info about a specific item.
    """
    item = session.query(Item).filter_by(id=item_id).one()
    return render_template('viewitem.html', item=item, session=login_session)


@app.route('/catalog/category/<int:category_id>/item/<int:item_id>/edit',
           methods=['GET', 'POST'])
def editItem(category_id, item_id):
    """
    editItem updates the Item in database.

    editItem redirects back to login page when user has not logged in. When
    request method is POST, item is updated to the database. When request method
    is GET, edititem.html page is rendered.

    args:
    category_id - ID of category
    item_id - ID of item

    return:
    redirects to showItems when method is POST or renders edititem.html template
    in case of GET method.
    """
    if 'username' not in login_session:
        return redirect('/login')
    item = session.query(Item).filter_by(id=item_id).one()
    category = session.query(Category).filter_by(id=category_id).one()
    if request.method == 'POST':
        newCategory = session.query(Category).filter_by(
            name=request.form['category']).one()
        item.name = request.form['name']
        item.description = request.form['description']
        item.category_id = newCategory.id
        session.add(item)
        session.commit()
        flash('Item %s is successfully updated.' % item.name)
        return redirect(url_for('showItems', category_id=category_id))
    else:
        categories = session.query(Category).all()
        return render_template('edititem.html', item=item,
                               category=category, categories=categories)


@app.route('/catalog/category/<int:category_id>/item/<int:item_id>/delete',
           methods=['GET', 'POST'])
def deleteItem(category_id, item_id):
    """
    deleteItem deletes the item from database.

    deleteItem redirects back to login page when user has not logged in. When
    request method is POST, item is deleted. When request method is GET,
    deleteItem.html page is rendered.

    args:
    category_id - ID of category
    item_id - ID of item

    return:
    redirects to showItems when method is POST or renders deleteItem.html
    template in case of GET method.
    """
    if 'username' not in login_session:
        return redirect('/login')
    item = session.query(Item).filter_by(id=item_id).one()
    category = session.query(Category).filter_by(id=category_id).one()
    if request.method == 'POST':
        session.delete(item)
        session.commit()
        flash('Item %s is successfully deleted.' % item.name)
        return redirect(url_for('showItems', category_id=category_id))
    else:
        return render_template('deleteitem.html', item=item)


@app.route('/catalog/item/new', methods=['GET', 'POST'])
def newItem():
    """
    newItem adds new Item to the database.

    newItem adds new Item to the database and redirects it to showItems url when
    method is POST. When method is GET, it renders newitem.html template.

    return:
    redirects to showItems url when method is POST else renders newitem.html
    template
    """
    if 'username' not in login_session:
        return redirect('/login')
    if request.method == 'POST':
        category = session.query(Category).filter_by(
            name=request.form['category']).one()
        newItem = Item(name=request.form['name'],
                       description=request.form['description'],
                       category_id=category.id,
                       user_id=getUserID(login_session['email']))
        session.add(newItem)
        session.commit()
        flash('Item %s is successfully added.' % newItem.name)
        return redirect(url_for('showItems', category_id=category.id))
    else:
        categories = session.query(Category).all()
        return render_template('newitem.html', categories=categories)


@app.route('/catalog/categoryList')
def getCategoryList():
    """
    getCategoryList returns the list of categories in JSON format.

    getCategoryList obtains category list from the database and further
    displays the same in JSON format.

    return:
    Category List in JSON format.
    """
    categories = session.query(Category).all()
    return jsonify({'Category':
                    [category.serialize for category in categories]})


@app.route('/catalog/category/<string:category_name>/itemsList')
def getItemsList(category_name):
    """
    getItemList returns the Items list of a specific category in JSON Format.

    getItemsList obtains items of a specific category from the database and
    futher returns the same in JSON format.

    args:
    category_name: name of category.

    return:
    List of Items of a specific category in JSON format.
    """
    category = session.query(Category).filter_by(name=category_name).one()
    items = session.query(Item).filter_by(category_id=category.id).all()
    return jsonify({'Category': category_name,
                    'item': [item.serialize for item in items]})


if __name__ == '__main__':
    app.secret_key = 'super_secret_key'
    app.debug = True
    app.run(host='0.0.0.0', port=8000)
