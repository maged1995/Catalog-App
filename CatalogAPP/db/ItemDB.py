from sqlalchemy import Column, Integer, String, ForeignKey
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy import create_engine
from passlib.apps import custom_app_context as pwd_context
Base = declarative_base()
import os


class customer(Base):
    __tablename__ = 'customer'
    user_id = Column(Integer, primary_key=True)
    username = Column(String(32), index=True)
    password_hash = Column(String(128))

    def hash_password(self, password):
        self.password_hash = pwd_context.encrypt(password)

    def verify_password(self, password):
        return pwd_context.verify(password, self.password_hash)


class Item(Base):
    __tablename__ = 'item'
    item_id = Column(Integer, primary_key=True)
    title = Column(String(32), index=True, unique=True)
    description = Column(String)
    creator_id = Column(Integer, ForeignKey("customer.user_id"), nullable=False)
    categ_id = Column(Integer, ForeignKey("category.Cat_id"), nullable=False)


class Category(Base):
    __tablename__ = 'category'
    Cat_id = Column(Integer, primary_key=True)
    name = Column(String(20), nullable=False)


engine = create_engine('postgresql://catalog:ps@localhost/items')


Base.metadata.create_all(engine)
