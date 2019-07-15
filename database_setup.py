#!/usr/bin/env python
"""
This python scripts sets up database for Item Catalog Application.

It creates database itemcatalog.db which has 3 tables - User, Category and
Item. User table has id, name, email and picture as columns. Category table has
id and name as columns. Item table has id, name, description, creation_date,
category_id and user_id as columns.
"""

import datetime
from sqlalchemy import create_engine, Column, ForeignKey
from sqlalchemy import Integer, String, DateTime
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship


Base = declarative_base()


class User(Base):
    """User class contains info about user like id, name, email and picture."""

    __tablename__ = 'user'

    id = Column(Integer, primary_key=True)
    name = Column(String(250), nullable=False)
    email = Column(String(250), nullable=False)
    picture = Column(String(250))

    @property
    def serialize(self):
        """Return User object data in easily serializeable format."""
        return {
            'name': self.name,
            'email': self.email,
            'picture': self.picture,
            'id': self.id
        }


class Category(Base):
    """Category class contains category info like id and name."""

    __tablename__ = 'category'

    id = Column(Integer, primary_key=True)
    name = Column(String(80), nullable=False, unique=True)

    @property
    def serialize(self):
        """Return Category object data in easily serializeable format."""
        return {
            'id': self.id,
            'name': self.name,
        }


class Item(Base):
    """Item class has item info like id, name, desc, date, catId and user_id."""

    __tablename__ = 'item'

    id = Column(Integer, primary_key=True)
    name = Column(String(80), nullable=False, unique=True)
    description = Column(String(250))
    creation_date = Column(DateTime, default=datetime.datetime.utcnow)
    category_id = Column(Integer, ForeignKey('category.id'))
    user_id = Column(Integer, ForeignKey('user.id'))
    category = relationship(Category)
    user = relationship(User)

    @property
    def serialize(self):
        """Return Item object data in easily serializeable format."""
        return {
            'id': self.id,
            'name': self.name,
            'description': self.description,
            'category_id': self.category_id
        }


engine = create_engine('sqlite:///itemcatalog.db')
Base.metadata.create_all(engine)
