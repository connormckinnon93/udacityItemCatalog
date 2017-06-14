# Based off UD330
import os
import sys
from sqlalchemy import Column, ForeignKey, Integer, String
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship
from sqlalchemy import create_engine

Base = declarative_base()


class User(Base):
    __tablename__ = 'user'

    # Don't save name since email will be our primary information retrieved
    id = Column(Integer, primary_key=True)
    email = Column(String(250), nullable=False)
    picture = Column(String(250))


class Category(Base):
    __tablename__ = 'category'

    id = Column(Integer, primary_key=True)
    name = Column(String(250), nullable=False)

    @property
    def serialize(self):
        """Return object data in easily serializeable format"""
        return {
            'id': self.id,
            'name': self.name,
        }


class Item(Base):
    __tablename__ = 'item'

    id = Column(Integer, primary_key=True)
    name = Column(String(250), nullable=False)
    description = Column(String(250), nullable=False)
    user_id = Column(Integer, ForeignKey('user.id'))
    user = relationship("User", cascade="delete")
    category_id = Column(Integer, ForeignKey('category.id'))
    category = relationship("Category", cascade="delete")

    # The name of the items category
    @property
    def return_cat_name(self):
        return self.category.name

    # The email of the user who created the item
    @property
    def return_user_name(self):
        return self.user.email

    @property
    def serialize(self):
        """Return object data in easily serializeable format"""
        return {
            'id': self.id,
            'item': self.name,
            'description': self.description,
            'category': self.return_cat_name,
            'user': self.return_user_name
        }


engine = create_engine('postgresql://grader:grader@localhost/catalog')
Base.metadata.create_all(engine)
