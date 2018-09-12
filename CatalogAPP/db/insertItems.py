#!/usr/bin/env python3
from ItemDB import customer, Category, Item
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

engine = create_engine('postgresql://catalog:ps@localhost/items')
DBSession = sessionmaker(bind=engine)
session = DBSession()


Category1 = Category(name='Soccer')
session.add(Category1)
session.commit()


Category2 = Category(name='Basketball')
session.add(Category2)
session.commit()


Category2 = Category(name='Baseball')
session.add(Category2)
session.commit()


Category2 = Category(name='Snowboarding')
session.add(Category2)
session.commit()


user1 = customer(username='maged95')
user1.hash_password('eagle')
session.add(user1)
session.commit()

Item1 = Item(title="Shinguards", description="IDK", creator_id=1, Category=1)
session.add(Item1)
session.commit()
