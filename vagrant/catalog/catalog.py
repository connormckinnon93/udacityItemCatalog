# Imports as recommended by Lesson 4 Part 2 in the UD330
# (https://github.com/udacity/ud330/tree/master/Lesson4/step2)
from flask import Flask, render_template, request
from flask import redirect, jsonify, url_for, flash
from sqlalchemy import create_engine, asc, desc
from sqlalchemy.orm import sessionmaker
from database_setup import Base, User, Category, Item
from flask import session as login_session
import random
import string
from oauth2client.client import flow_from_clientsecrets
from oauth2client.client import FlowExchangeError
import httplib2
import json
from flask import make_response
import requests

# Create Flask APP
app = Flask(__name__)

# Load client information for Google Credentials API
CLIENT_ID = json.loads(open('client_secrets.json', 'r').read())[
    'web']['client_id']
APPLICATION_NAME = "Restaurant Menu Application"

# Connect to Database
engine = create_engine('postgresql://grader:grader@localhost/catalog')
Base.metadata.bind = engine

# Create Database session
DBSession = sessionmaker(bind=engine)
session = DBSession()

# Dispaly all categories and latest items


@app.route('/')
@app.route('/catalog/')
def showCatalog():
    # Return all categories
    categories = session.query(Category).order_by(asc(Category.name))
    # Return last 5 items bv ID
    items = session.query(Item).order_by(desc(Item.id)).limit(5)
    # Check if there is a user present
    if 'username' not in login_session:
        # If there is no user present offer public catalog
        return render_template('publicCatalog.html',
                               categories=categories, items=items)
    else:
        # If there is a user present offer catalog with ability to add items
        return render_template('catalog.html',
                               categories=categories, items=items)


# Display a specific category
@app.route('/catalog/<int:category_id>')
@app.route('/catalog/<int:category_id>/items')
def showCategory(category_id):
    # Return all categories
    categories = session.query(Category).order_by(asc(Category.name))
    # Return the specifically open category
    open_category = session.query(
        Category).filter_by(id=category_id).one().name
    # Return all items associated with open category
    items = session.query(Item).filter_by(category_id=category_id).all()
    # Count number of items returned
    item_count = len(items)
    # Return a view of the invidual category and relevant informaiton
    return render_template('category.html', categories=categories,
                           open_category=open_category, items=items,
                           item_count=item_count)

# Display a specific item


@app.route('/catalog/<int:category_id>/<int:item_id>')
def showItem(category_id, item_id):
    # Return just the searched for item
    item = session.query(Item).filter_by(id=item_id).one()
    # Return a view of the searched for item
    if 'username' not in login_session:
        return render_template('publicItem.html', item=item)
    else:
        return render_template('item.html', item=item)

# Create new item


@app.route('/catalog/item/create', methods=['GET', 'POST'])
def createItem():
    # Check for user in sesion and redirect to login if absent
    if 'username' not in login_session:
        return redirect(url_for('showLogin'))
    else:
        # If being posted to try and create a new item
        if request.method == 'POST':
            try:
                # Create a new item with SQLAlchemy using POST information
                newItem = Item(name=request.form['name'],
                               description=request.form['description'],
                               category_id=request.form['category'],
                               user_id=login_session['user_id'])
                session.add(newItem)
                session.commit()
                # Let the user now it was successfully added and then redirect
                # to frontpage
                flash('%s successfully added!' % (newItem.name))
                return redirect(url_for('showCatalog'))
            # If the new object couldn't be added then let the user know
            except:
                flash('Not added added due to error!')
                return redirect(url_for('createItem'))
        else:
            # Return all categories in alphabetical order for GET requests
            categories = session.query(Category).order_by(asc(Category.name))
            # Return view for form to create a new item
            return render_template('createItem.html', categories=categories)

# Update a item


@app.route('/catalog/<int:category_id>/<int:item_id>/update',
           methods=['GET', 'POST'])
def updateItem(category_id, item_id):
    # Check for user in session
    if 'username' not in login_session:
        # If no user present redirect to login and let them know
        flash('You need to login first!')
        return redirect(url_for('showLogin'))
    # Load the item they are trying to edit
    itemToEdit = session.query(Item).filter_by(id=item_id).one()
    # Check to see if the user owns this item
    if login_session['user_id'] != itemToEdit.user_id:
        # Let them know they don't have permission and give them a chance to
        # change accounts
        flash('You do not have permission to edit this item!')
        return redirect(url_for('showLogin'))
    else:
        # If the user does own this item update it to match form information
        if request.method == 'POST':
            # Try to update the item with post contents
            try:
                itemToEdit.name = request.form['name']
                itemToEdit.description = request.form['description']
                itemToEdit.category_id = request.form['category']
                session.add(itemToEdit)
                session.commit()
                flash('%s successfully updated!' % (itemToEdit.name))
                return redirect(url_for('showCatalog'))
            # If there is an error let them know and then retry
            except:
                flash('Not updated due to an error')
                return redirect(url_for('updateItem',
                                        item_id=itemToEdit.id,
                                        category_id=category_id))
        # If using the GET method return the form to edit this item
        else:
            categories = session.query(Category).order_by(asc(Category.name))
            return render_template('editItem.html',
                                   categories=categories, item=itemToEdit)

# Delete an item


@app.route('/catalog/<int:category_id>/<int:item_id>/delete',
           methods=['GET', 'POST'])
def deleteItem(category_id, item_id):
    # Check for user
    if 'username' not in login_session:
        # If no user present tell them they need to login first and then let
        # them try
        flash('You need to login first!')
        return redirect(url_for('showLogin'))
    # Load the item to be deleted
    itemToDelete = session.query(Item).filter_by(id=item_id).one()
    # Check if user is owner of item and if not notify them and let them
    # change account
    if login_session['user_id'] != itemToDelete.user_id:
        flash('You do not have permission to edit this item!')
        return redirect(url_for('showLogin'))
    # If user is owner
    else:
        # If method is POST
        if request.method == 'POST':
            # try to delete item
            try:
                session.delete(itemToDelete)
                session.commit()
                flash('%s successfully deleted!' % (itemToDelete.name))
                return redirect(url_for('showCatalog'))
            # if error occurs let them know and then let them try again
            except:
                flash('Unable to delete item due to error')
                return redirect(url_for('deleteItem',
                                        item_id=itemToDelete.id,
                                        category_id=category_id))
        # If method is GET return a view with the confirmation page to delete
        else:
            return render_template('deleteItem.html', item=itemToDelete)

# Create anti-forgery state token


@app.route('/login')
def showLogin():
    # Create CSFR token
    state = ''.join(random.choice(string.ascii_uppercase + string.digits)
                    for x in xrange(32))
    # Save token
    login_session['state'] = state
    # Return the login view
    return render_template('login.html', state=state)

# USER HELPER FUNCTIONS

# Use SQLAlchemy to create a new user object and save it


def createUser(login_session):
    # Try and create a new user return None if failed
    try:
        # Pass information in from login_session
        newUser = User(email=login_session[
                       'email'], picture=login_session['picture'])
        session.add(newUser)
        session.commit()
        # Find user by email
        user = session.query(User).filter_by(
            email=login_session['email']).one()
        # Return user.id
        return user.id
    except:
        return None

# Use SQLAlchemy to search for user by ID return None if not found


def getUserInfo(user_id):
    try:
        user = session.query(User).filter_by(id=user_id).one()
        return user
    except:
        return None

# Use SQLAlchemy to search for User ID by email and return None if not found


def getUserID(email):
    try:
        user = session.query(User).filter_by(email=email).one()
        return user.id
    except:
        return None

# Sign in using Google Account
# Taken and upgraded from UD330 Lesson 12


@app.route('/gconnect', methods=['POST'])
def gconnect():
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
    url = ('https://www.googleapis.com/oauth2/v1/tokeninfo?access_token=%s' %
           access_token)
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

    stored_credentials = login_session.get('credentials')
    stored_gplus_id = login_session.get('gplus_id')
    if stored_credentials is not None and gplus_id == stored_gplus_id:
        response = make_response(json.dumps(
            'Current user is already connected.'),
            200)
        response.headers['Content-Type'] = 'application/json'
        return response

    # Store the access token in the session for later use.
    login_session['access_token'] = credentials.access_token
    login_session['gplus_id'] = gplus_id

    # Get user info
    userinfo_url = "https://www.googleapis.com/oauth2/v1/userinfo"
    params = {'access_token': credentials.access_token, 'alt': 'json'}
    # had to add requests module in Vagrant box
    answer = requests.get(userinfo_url, params=params)

    data = answer.json()

    login_session['username'] = data['name']
    login_session['picture'] = data['picture']
    login_session['email'] = data['email']
    # ADD PROVIDER TO LOGIN SESSION (this can be expanded to include other
    # providers later)
    login_session['provider'] = 'google'

    # see if user exists, if it doesn't make a new one
    user_id = getUserID(data["email"])
    if not user_id:
        user_id = createUser(login_session)
    login_session['user_id'] = user_id

    # Create an HTML response (this seems like a poo method of doing so... is
    # it possible to use JINJA2)
    output = ''
    output += '<h1>Welcome, '
    output += login_session['username']
    output += '!</h1>'
    output += '<img src="'
    output += login_session['picture']
    output += ' " style = "width: 150px; height: 150px;border-radius: 75px;'
    output += '-webkit-border-radius: 75px;-moz-border-radius: 75px;"> '
    # Output is returned in successful callback
    return output

# Taken and upgraded from UD330 Lesson 12


@app.route('/gdisconnect')
def gdisconnect():
    # Only disconnect a connected user.
    credentials = login_session.get('credentials')
    if credentials is None:
        response = make_response(
            json.dumps('Current user not connected.'), 401)
        response.headers['Content-Type'] = 'application/json'
        return response
    # cannot store full credentials just grab access token
    access_token = credentials.access_token
    url = 'https://accounts.google.com/o/oauth2/revoke?token=%s' % access_token
    h = httplib2.Http()
    result = h.request(url, 'GET')[0]
    if result['status'] != '200':
        # For whatever reason, the given token was invalid.
        response = make_response(
            json.dumps('Failed to revoke token for given user.'), 400)
        response.headers['Content-Type'] = 'application/json'
        return response

# Disconnect based on provider


@app.route('/disconnect')
def disconnect():
        # check to see if provider is listed
    if 'provider' in login_session:
        # Could be expanded later to include multiple providers
        if login_session['provider'] == 'google':
            # Will need a unique disconnect for each provider
            gdisconnect()
            del login_session['gplus_id']
            del login_session['access_token']
        del login_session['username']
        del login_session['email']
        del login_session['picture']
        del login_session['user_id']
        del login_session['provider']
        flash('You have logged out.')
        return redirect(url_for('showCatalog'))
    # If there is no provider the disconnect method wont work
    else:
        flash('The logout was not successful')
        return redirect(url_for('showCatalog'))

# JSON APIs to view Category Information


@app.route('/catalog/categories/JSON')
def categoriesJSON():
        # Get all categories and order them by name
    categories = session.query(Category).order_by(asc(Category.name))
    # Return a json object by serializing each entry
    return jsonify(Categories=[i.serialize for i in categories])

# JSON APIs to view Items Information


@app.route('/catalog/items/JSON')
def itemsJSON():
        # Get all items and order them by id
    items = session.query(Item).order_by(desc(Item.id))
    # Return a json object by serializing each entry
    return jsonify(Items=[i.serialize for i in items])

# JSON APIs to view individual Category Information


@app.route('/catalog/category/<int:category_id>/JSON')
def categoryJSON(category_id):
        # Get the category being searched for
    category = session.query(Category).filter_by(id=category_id).one()
    # If category exists return it as json object
    if category:
        return jsonify(Category=category.serialize)
    # If category doesn't exist redirect and let them know
    else:
        flash('Category does not exist')
        return redirect(url_for('showCatalog'))

# JSON APIs to view individual Item Information


@app.route('/catalog/item/<int:item_id>/JSON')
def itemJSON(item_id):
        # Get the item being searched for
    item = session.query(Item).filter_by(id=item_id).one()
    # If item exists return it as json object
    if item:
        return jsonify(Item=item.serialize)
    # If item doesn't exist redirect and let them know
    else:
        flash('Item does not exist')
        return redirect(url_for('showCatalog'))

# Export the Flask app on localhost and port 5000
if __name__ == '__main__':
    app.secret_key = 'super_secret_key'
    app.debug = True
    app.run(host='0.0.0.0', port=5000)
