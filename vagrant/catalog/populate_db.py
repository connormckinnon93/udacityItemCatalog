from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from database_setup import Base, User, Category, Item

engine = create_engine('sqlite:///itemcatalog.db')
# Bind the engine to the metadata of the Base class so that the
# declaratives can be accessed through a DBSession instance
Base.metadata.bind = engine

DBSession = sessionmaker(bind=engine)
# A DBSession() instance establishes all conversations with the database
# and represents a "staging zone" for all the objects loaded into the
# database session object. Any change made against the objects in the
# session won't be persisted into the database until you call
# session.commit(). If you're not happy about the changes, you can
# revert all of them back to the last commit by calling
# session.rollback()
session = DBSession()

# Create dummy user
User1 = User(name="Connor", email="mckinnondconnor@gmail.com",
             picture='')
session.add(User1)
session.commit()

# Create categories
category1 = Category(name="Soccer", description="This is just a dummy description")
session.add(category1)
session.commit()

category2 = Category(name="Basketball", description="This is just a dummy description")
session.add(category2)
session.commit()

category3 = Category(name="Baseball", description="This is just a dummy description")
session.add(category3)
session.commit()

category4 = Category(name="Frisbee", description="This is just a dummy description")
session.add(category4)
session.commit()

category5 = Category(name="Snowboarding", description="This is just a dummy description")
session.add(category5)
session.commit()

category6 = Category(name="Rock Climbing", description="This is just a dummy description")
session.add(category6)
session.commit()

category7 = Category(name="Foosball", description="This is just a dummy description")
session.add(category7)
session.commit()

category8 = Category(name="Skating", description="This is just a dummy description")
session.add(category8)
session.commit()

category9 = Category(name="Hockey", description="This is just a dummy description")
session.add(category9)
session.commit()

#Create items for categories
item1 = Item(name="Demo1", description="This is just a dummy description", user_id=1, category_id=1)
session.add(item1)
session.commit()

item2 = Item(name="Demo2", description="This is just a dummy description", user_id=1, category_id=2)
session.add(item2)
session.commit()

item3 = Item(name="Demo3", description="This is just a dummy description", user_id=1, category_id=3)
session.add(item3)
session.commit()

item4 = Item(name="Demo4", description="This is just a dummy description", user_id=1, category_id=4)
session.add(item4)
session.commit()

item5 = Item(name="Demo5", description="This is just a dummy description", user_id=1, category_id=5)
session.add(item5)
session.commit()

item6 = Item(name="Demo6", description="This is just a dummy description", user_id=1, category_id=6)
session.add(item6)
session.commit()

item7 = Item(name="Demo7", description="This is just a dummy description", user_id=1, category_id=7)
session.add(item7)
session.commit()

item8 = Item(name="Demo8", description="This is just a dummy description", user_id=1, category_id=8)
session.add(item8)
session.commit()

item9 = Item(name="Demo9", description="This is just a dummy description", user_id=1, category_id=9)
session.add(item9)
session.commit()