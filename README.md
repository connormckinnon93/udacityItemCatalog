# Udacity Project Item Catalog

**Program**: Udacity Fullstack Web Developer Nanodegree

**Project 5:** Item Catalog

**Languages/Frameworks:** Python 2.7.x, SQLite, SQLAlchemy, Flask, Google Credentials Manager

**Methodology:** OOP

## Dependencies

This project runs inside the a modified version of the Fullstack Nanodegree VM.

Libraries included in this project are:
- Source code from for Fullstack Nanodegree VM: (https://github.com/udacity/fullstack-nanodegree-vm)
- Git: (https://git-scm.com/downloads)
- VirtualBox: (https://www.virtualbox.org/wiki/Downloads)
- Vagrant: (https://www.vagrantup.com/downloads.html)
- Python 2.7.x: (https://www.python.org/)
- SQLAlchemy: (http://www.sqlalchemy.org/)
- SQLite: (https://www.sqlite.org/)
- Flask: (http://flask.pocoo.org/)


## Getting Started

The project is located under `/vagrant/catalog`.

It contains the follow files and folders:
- catalog.py
- database_setup.py
- populate_db.py
- client_secrets.json
- static
- templates

*catalog.py*
Contains the main Flask application which when run access the DBs and creates a web server on localhost:5000

*database_setup.py*
Contains python and SQLAlchemy code to create the SQLite database

*populate_db.py*
Contains python and SQLAlchemy used to add the categories to the database

*client_secrets.json*
Contains the client information for the Google Credential Manager

*static*
Contains the static resource files like CSS and JS

*templates*
Contains the JINJA templates and partials

### Using the Virtual Machine

In order to get started with the virtual machine follow these steps in your preferred BASH terminal from the root folder.

```
vagrant up
vagrant ssh
cd /vagrant/catalog
python catalog.py
```

You can now access the application at `localhost:5000`

The JSON endpoints are located at:
- localhost:5000/catalog/categories/JSON (Return all categories)
- localhost:5000/catalog/items/JSON (Return all categories)
- localhost:5000/catalog/category/category_id/JSON (Returns the JSON for the category at category_id when it is a viable int)
- localhost:5000/catalog/item/item_id/JSON (Returns the JSON for the item at item_id when it is a viable int))