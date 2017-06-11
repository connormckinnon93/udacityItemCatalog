# Imports as recommended by Lesson 4 Part 2 in the UD330 (https://github.com/udacity/ud330/tree/master/Lesson4/step2)
from flask import Flask, render_template, request, redirect, jsonify, url_for, flash
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
CLIENT_ID = json.loads(open('client_secrets.json', 'r').read())['web']['client_id']
APPLICATION_NAME = "Restaurant Menu Application"

# Connect to Database
engine = create_engine('sqlite:///itemcatalog.db')
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
		return render_template('publicCatalog.html', categories = categories, items = items)
	else:
		# If there is a user present offer catalog with ability to add items
		return render_template('catalog.html', categories = categories, items = items)


# Display a specific category
@app.route('/catalog/<int:category_id>')
@app.route('/catalog/<int:category_id>/items')
def showCategory(category_id):
	# Return all categories
	categories = session.query(Category).order_by(asc(Category.name))
	# Return the specifically open category
	open_category = session.query(Category).filter_by(id = category_id).one().name
	# Return all items associated with open category
	items = session.query(Item).filter_by(category_id = category_id).all()
	# Count number of items returned
	item_count = len(items)
	return render_template('category.html', categories = categories, open_category = open_category, items = items, item_count = item_count)

# Display a specific item
@app.route('/catalog/<int:category_id>/<int:item_id>')
def showItem(category_id, item_id):
	item = session.query(Item).filter_by(id = item_id).one()
	return render_template('item.html', item = item)

# Create new item
@app.route('/catalog/item/create', methods = ['GET', 'POST'])
def createItem():
	if 'username' not in login_session:
		return redirect(url_for('showLogin'))
	else:
		if request.method == 'POST':
			newItem = Item(name = request.form['name'], description = request.form['description'], category_id = request.form['category'], user_id = login_session['user_id'])
			session.add(newItem)
			session.commit()
			flash('%s successfully added!' % (newItem.name))
			return redirect(url_for('showCatalog'))
		else:
			categories = session.query(Category).order_by(asc(Category.name))
			return render_template('createItem.html', categories = categories)

# Update a item
@app.route('/catalog/<int:category_id>/<int:item_id>/update', methods = ['GET', 'POST'])
def updateItem(category_id, item_id):
	if 'username' not in login_session:
		flash('You need to login first!')
		return redirect(url_for('showLogin'))
	itemToEdit = session.query(Item).filter_by(id = item_id).one()
	if login_session['user_id'] != itemToEdit.user_id:
		flash('You do not have permission to edit this item!')
		return redirect(url_for('showLogin'))
	else:
		if request.method == 'POST':
			itemToEdit.name = request.form['name']
			itemToEdit.description = request.form['description']
			itemToEdit.category_id = request.form['category']
			session.add(itemToEdit)
			session.commit()
			flash('%s successfully updated!' % (itemToEdit.name))
			return redirect(url_for('showCatalog'))
		else:
			categories = session.query(Category).order_by(asc(Category.name))
			return render_template('editItem.html', categories = categories, item = itemToEdit)

# Delete an item
@app.route('/catalog/<int:category_id>/<int:item_id>/delete', methods = ['GET', 'POST'])
def deleteItem(category_id, item_id):
	if 'username' not in login_session:
		flash('You need to login first!')
		return redirect(url_for('showLogin'))
	itemToDelete = session.query(Item).filter_by(id=item_id).one()
	if login_session['user_id'] != itemToDelete.user_id:
		flash('You do not have permission to edit this item!')
		return redirect(url_for('showLogin'))
	else:
		if request.method == 'POST':
			session.delete(itemToDelete)
			session.commit()
			flash('%s successfully deleted!' % (itemToDelete.name))
			return redirect(url_for('showCatalog'))
		else:
			return render_template('deleteItem.html', item = itemToDelete)

# Create anti-forgery state token
@app.route('/login')
def showLogin():
    state = ''.join(random.choice(string.ascii_uppercase + string.digits) for x in xrange(32))
    login_session['state'] = state
    return render_template('login.html', state = state)

# User Helper Functions
def createUser(login_session):
    newUser = User(email=login_session['email'], picture=login_session['picture'])
    session.add(newUser)
    session.commit()
    user = session.query(User).filter_by(email=login_session['email']).one()
    return user.id


def getUserInfo(user_id):
    user = session.query(User).filter_by(id=user_id).one()
    return user


def getUserID(email):
    try:
        user = session.query(User).filter_by(email=email).one()
        return user.id
    except:
    	return None

# Sign in using Google Account
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
    url = ('https://www.googleapis.com/oauth2/v1/tokeninfo?access_token=%s' % access_token)
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
        response = make_response(json.dumps('Current user is already connected.'),
                                 200)
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
    # ADD PROVIDER TO LOGIN SESSION
    login_session['provider'] = 'google'

    # see if user exists, if it doesn't make a new one
    user_id = getUserID(data["email"])
    if not user_id:
        user_id = createUser(login_session)
    login_session['user_id'] = user_id

    output = ''
    output += '<h1>Welcome, '
    output += login_session['username']
    output += '!</h1>'
    output += '<img src="'
    output += login_session['picture']
    output += ' " style = "width: 300px; height: 300px;border-radius: 150px;-webkit-border-radius: 150px;-moz-border-radius: 150px;"> '
    return output

@app.route('/gdisconnect')
def gdisconnect():
    # Only disconnect a connected user.
    credentials = login_session.get('credentials')
    if credentials is None:
        response = make_response(
            json.dumps('Current user not connected.'), 401)
        response.headers['Content-Type'] = 'application/json'
        return response
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
    if 'provider' in login_session:
        if login_session['provider'] == 'google':
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
    else:
    	flash('The logout was not successful')
        return redirect(url_for('showCatalog'))

# JSON APIs to view Category Information
@app.route('/catalog/categories/JSON')
def categoriesJSON():
    categories = session.query(Category).order_by(asc(Category.name))
    return jsonify(Categories=[i.serialize for i in categories])

# JSON APIs to view Items Information
@app.route('/catalog/items/JSON')
def itemsJSON():
    items = session.query(Item).order_by(desc(Item.id))
    return jsonify(Items=[i.serialize for i in items])

# JSON APIs to view individual Category Information
@app.route('/catalog/category/<int:category_id>/JSON')
def categoryJSON(category_id):
    category = session.query(Category).filter_by(id = category_id).one()
    return jsonify(Category=category.serialize)

# JSON APIs to view individual Item Information
@app.route('/catalog/item/<int:item_id>/JSON')
def itemJSON(item_id):
    item = session.query(Item).filter_by(id = item_id).one()
    return jsonify(Item=item.serialize)

if __name__ == '__main__':
    app.secret_key = 'super_secret_key'
    app.debug = True
    app.run(host='0.0.0.0', port=5000)