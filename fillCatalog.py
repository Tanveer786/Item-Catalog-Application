#!/usr/bin/env python
"""
This python script fills the itemcatalog.db database with some info.

It creates a dummy user and adds it to database. Similarly adds category list
and also items in some of the categories.
"""

import sys
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from database_setup import Base, Category, Item, User

engine = create_engine('sqlite:///itemcatalog.db')
Base.metadata.bind = engine

DBSession = sessionmaker(bind=engine)
session = DBSession()

categories = ['Soccer', 'Basketball', 'Baseball', 'Frisbee', 'Snow Climbing',
              'Rock Climbing', 'Foosball', 'Skating', 'Hockey']

ItemsInEachCategory = {
    'Soccer': [['Football', 1, '''the ball used in the sport of association
                football. A black-and-white patterned truncated icosahedron
                design, brought to prominence by the Adidas Telstar, has become
                an icon of the sport.'''],
               ['Cleats', 2, '''Cleats or studs are protrusions on the sole of
                a shoe, or on an external attachment to a shoe, that provide
                additional traction on a soft or slippery surface''']],
    'Basketball': [['Basketball', 3, '''A basketball is a spherical ball used
                    in basketball games. The ball must be very durable and easy
                    to hold on to'''],
                   ['Breakaway rim', 4, '''A breakaway rim is a basketball rim
                     that contains a hinge and a spring at the point where it
                     attaches to the backboard so that it can bend downward
                     when a player dunks a basketball''']],
    'Baseball': [['Bat', 5, '''A rounded, solid wooden or hollow aluminum bat.
                  Wooden bats are traditionally made from ash wood, though
                  maple and bamboo is also sometimes used'''],
                 ['Catcher\'s mitt', 6, '''Leather mitt worn by catchers. It is
                  much wider than a normal fielder\'s glove and the four
                  fingers are connected.''']],
    'Frisbee': [['Flying disc', 7, '''is a gliding toy or sporting item that is
                 generally plastic and roughly 8 to 10 inches (20 to 25 cm) in
                 diameter with a pronounced lip''']]
}

# Add a dummy user to database
user = User(id=1, name='Dummy',
            picture='https://img.icons8.com/windows/32/000000/contacts.png',
            email='dummy@gmail.com')
session.add(user)
session.commit()

# Add category list to database
for category_name in categories:
    category = Category(name=category_name)
    session.add(category)
    session.commit()

# Add items for some of the categories
for category in ItemsInEachCategory:
    currentCategory = session.query(Category).filter_by(name=category).one()
    for item in ItemsInEachCategory[category]:
        newItem = Item(name=item[0], id=item[1], description=item[2],
                       category=currentCategory, user=user)
        session.add(newItem)
        session.commit()
