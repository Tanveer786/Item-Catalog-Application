# Project: Item-Catalog-Application
  This project is develop a web application that provides a list of items within a variety of categories as well as provide user registration and authentication. Registered users will have the ability to post, edit and delete their own items. The entire application (Frontend and Backend) is built from scratches.
  
 ## Getting Started
Follow the prerequisites section to get the setup ready. Then following commands must be given :
  1. `python database_setup.py` - To Create the database
  2. `python fillCatalog.py` - Fills the database with Categories and few sample items
  3. `python application.py` - Hosts the web application on localhost:8000
 
Open a browser and type the URL http://localhost:8000 to access the application.

## Prerequisites
Following softwares must be installed prior to running the application:
  1. [Virtual box](https://www.virtualbox.org/wiki/Download_Old_Builds_5_1)
  2. [Vagrant](https://www.vagrantup.com/downloads.html)
  3. [Udacity Vagrant File](https://github.com/udacity/fullstack-nanodegree-vm) - Follow the instructions as given in the link to setup the vagrant.
 
 Clone this repo and paste it inside /vagrant/ folder.
 
 ## Technology used
 ### Frontend
 * Bootstrap framework is used along with HTML & CSS for ease of designing layout and making it responsive(Mobile-friendly).
 * Flask Template inheritance is used to create a skeleton layout consisting of all common elements of the site and define blocks which child templates can override.
 ### Backend
 * Flask, a lightweight WSGI web application framework in python is used to implement the server, handle the CRUD operations, Routing, Message flashing and provide JSON endpoints.
 * SQLite3 database is used. Flask SQLAlchemy library is used to communicate with database for CRUD operations.
 * User Registration and Authentication is performed using third party OAuth service - *Google*
 
 ## How to use the Application
 * Login into the Application by clicking on the Login button and sign in using Google.
 * After Login is Successful, any of the below operations can be done by the user :
    * Add an item in any of the categories by clicking on "Add New Item" button which displays a form that needs to be filled.
    * View item by clicking on item link.
    * Edit any of the item added by user by clicking on Edit button and making changes to the Item form.
    * Delete any of the item added by used by clicking on Delete button.
 * Once all the operations are performed, User can log out of the application by clicking on User name, then logout.
 
 ## JSON Endpoints
 * Following JSON endpoints have been provided:
    * /catalog/categoryList - Returns the list of categories.
    * /catalog/category/<category_name>/itemsList - Returns the list of items within that category.
 
 ## Author
 * __Tanveer Ahmed__
 
