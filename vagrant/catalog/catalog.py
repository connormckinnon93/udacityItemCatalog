# Imports as recommended by Lesson 4 Part 2 in the UD330 (https://github.com/udacity/ud330/tree/master/Lesson4/step2)
from flask import Flask, render_template, request, redirect, jsonify, url_for, flash
from sqlalchemy import create_engine, asc
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

app = Flask(__name__)

# Connect to Database and create database session
engine = create_engine('sqlite:///itemcatalog.db')
Base.metadata.bind = engine

DBSession = sessionmaker(bind=engine)
session = DBSession()

# Dispaly all categories and latest items
@app.route('/')
@app.route('/catalog/')
def showCatalog():
	categories = session.query(Category).all()
	items = session.query(Item).all()
	return render_template('catalog.html', categories = categories, items = items)

# Display a specific category
@app.route('/catalog/<int:category_id>')
@app.route('/catalog/<int:category_id>/items')
def showCategory(category_id):
	return render_template('category.html')

# Display a specific item
@app.route('/catalog/<int:category_id>/<int:item_id>')
def showItem(category_id, item_id):
	return render_template('item.html')

# Create new item
@app.route('/catalog/<int:category_id>/<int:item_id>/create')
def createItem(category_id, item_id):
	return render_template('newItem.html')

# Update a item
@app.route('/catalog/<int:category_id>/<int:item_id>/update')
def updateItem(category_id, item_id):
	return render_template('editItem.html')

# Delete an item
@app.route('/catalog/<int:category_id>/<int:item_id>/delete')
def deleteItem(category_id, item_id):
	return render_template('deleteItem.html')

if __name__ == '__main__':
    app.secret_key = 'super_secret_key'
    app.debug = True
    app.run(host='0.0.0.0', port=5000)