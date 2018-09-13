#!/usr/bin/env python3
import sys
sys.path.insert(1 , '/var/www/FLASKAPPS/CatalogAPP/db')
sys.stdout = open('/var/www/FLASKAPPS/CatalogAPP/output.txt', 'w')
from ItemDB import Base, customer, Category, Item
from flask import Flask, jsonify, request, url_for, redirect, flash
# from flask_dance.contrib.github import make_github_blueprint, github
from sqlalchemy.orm import sessionmaker
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import create_engine, asc, text
from flask import session as login_session, render_template
from flask_httpauth import HTTPBasicAuth
from oauth2client.client import flow_from_clientsecrets
from oauth2client.client import FlowExchangeError
import random
import string
import httplib2
import json
from flask import make_response
import requests
from sqlalchemy.pool import StaticPool
from collections import OrderedDict
import os

auth = HTTPBasicAuth()

engine = create_engine('postgresql://catalog:ps@localhost/items',
                       poolclass=StaticPool)

Base.metadata.bind = engine
DBSession = sessionmaker(bind=engine)
session = DBSession()
app = Flask(__name__)
db = SQLAlchemy(app)
app.config['JSON_SORT_KEYS'] = False
CLIENT_ID = json.loads(
    open('/var/www/FLASKAPPS/CatalogAPP/client_secrets.json', 'r').read())['web']['client_id']


# this is the main page
@app.route('/')
def showAll():
    # loads all categories
    categories = session.query(Category).order_by(asc(Category.name))
    # and loads all items, each with it's own Category
    sql = text('select title,name,' +
               'item_id, item.categ_id from item ' +
               'join Category on item.categ_id=category.categ_id;')
    Items = engine.execute(sql)
    return render_template('publicPage.html',
                           Categories=categories, Items=Items)


# this page loads all categories and only the items that are in the
# selected category
@app.route('/catalog/<string:name>/items')
def showCat(name):
    # loads all items of the selected category
    categories = session.query(Category).filter_by(name=name).all()
    Items = session.query(Item).filter_by(categ_id=categories[0].categ_id).all()
    # loads all categories
    categories = session.query(Category).order_by(asc(Category.name))
    return render_template('publicCat.html',
                           Categories=categories, Items=Items)


# this page views an item with all its information
@app.route('/catalog/<string:name>/<string:title>')
def showDesc(name, title):
    # loads the item by name
    item = session.query(Item).filter_by(title=title).all()
    try:
        print(login_session['username'])
        u = session.query(customer).filter_by(
            username=login_session['username']).all()
        return render_template('itemDesc.html', item=item, User=u)
    except:
        return render_template('itemDesc.html', item=item)


# this pages loads the login
@app.route('/login', methods=['GET', 'POST'])
def showLogin():
    # if the form is being viewed then we'll also need to check if the user is
    # already signed in
    if request.method == 'GET':
        # if so then the word logout would have been displayed and this part
        # of the code will remove all user data from the login session
        if login_session:
            if 'provider' in login_session:
                # deletes the information from the login session that is
                # retrieved by a provider
                if login_session['provider'] == 'google':
                    # assuming that we have other providers
                    gdisconnect()
                    del login_session['gplus_id']
                    del login_session['access_token']
                    del login_session['provider']
            try:
                del login_session['username']
                try:
                    del login_session['password']
                except:
                    return redirect('/')
                return redirect('/')
            # if there is no username or password in the session then there's
            # no login in, which means that i can view the page
            # and create a new state
            except:
                state = ''.join(random.choice(string.ascii_uppercase +
                                string.digits) for x in range(32))
                login_session['state'] = state
                return render_template('signIn.html', STATE=state)
        # starts a new login session with new a state
        else:
            state = ''.join(random.choice(string.ascii_uppercase +
                            string.digits) for x in range(32))
            login_session['state'] = state
            return render_template('signIn.html', STATE=state)
    # at this condition, it means that the method is post and we're using the
    # local method of signin or signup
    else:
        # searches for the username
        us = session.query(customer).filter_by(
             username=request.form['username']).all()
        # if the username is not in database, then we'll sign up
        if not us:
            # local signup is not allowed to have an empty password
            if request.form['password'] == '':
                return redirect("/login", code=400)
            # creating a new user record
            newuser = customer(username=request.form['username'])
            newuser.hash_password(request.form['password'])
            session.add(newuser)
            session.commit()
            login_session['username'] = request.form['username']
            login_session['password'] = request.form['password']
            return redirect('/')
        #  if user is in database then we'll verify
        else:
            # if password is empty, then it's a google account which only needs
            # google verification
            if us[0].verify_password(''):
                return redirect("/login", code=400)
            # if password is wrong
            elif not us[0].verify_password(request.form['password']):
                return redirect("/login", code=400)
            # if password is right
            else:
                login_session['username'] = request.form['username']
                login_session['password'] = request.form['password']
                return redirect('/')


@app.route('/catalog/<string:title>/edit', methods=['POST', 'GET'])
def editItem(title):
    # in the try except, we're ensuring that the user is logged in
    # else, no one's allowed to edit
    try:
        login_session['username']
    except:
        return redirect(url_for('showAll'))
    u = session.query(customer).filter_by(username=login_session['username']).all()
    item = session.query(Item).filter_by(title=title).all()
    if request.method == 'GET':
        if u[0].user_id == item[0].creator_id:
            categories = session.query(Category).order_by(asc(Category.name))

            return render_template('edititem.html',
                                   Categories=categories, Item=item)
        else:
            return redirect(url_for('showAll'))
    else:
        itemEdit = session.query(Item).filter_by(title=title).one()
        itemEdit.title = request.form['title']
        itemEdit.description = request.form['description']
        itemEdit.categ_id = request.form['Category']
        session.commit()
        return redirect(url_for('showAll'))


@app.route('/catalog/<string:title>/delete', methods=['post', 'get'])
def deleteItem(title):
    # in the try except, we're ensuring that the user is logged in
    # else, no one's allowed to delete
    try:
        login_session['username']
    except:
        return redirect(url_for('showAll'))
    u = session.query(customer).filter_by(username=login_session['username']).all()
    item = session.query(Item).filter_by(title=title).all()
    if u[0].user_id == item[0].creator_id:
        if request.method == 'GET':
            return render_template('deleteItem.html', Item=item)
        elif request.method == 'POST':
            itemDelete = session.query(Item).filter_by(title=title).one()
            session.delete(itemDelete)
            session.commit()
    return redirect(url_for('showAll'))


@app.route('/catalog/Add', methods=['post', 'get'])
def addItem():
    # in the try except, we're ensuring that the user is logged in
    # else, no one's allowed to add
    try:
        login_session['username']
    except:
        return redirect(url_for('showAll'))
    if request.method == 'GET':
        categories = session.query(Category).order_by(asc(Category.name))
        return render_template('additem.html', Categories=categories)
    elif request.method == 'POST':
        u = session.query(customer).filter_by(
            username=login_session['username']).one()
        itemadd = Item(title=request.form['title'],
                       description=request.form['description'],
                       categ_id=request.form['Category'],
                       creator_id=u.user_id)
        session.add(itemadd)
        session.commit()
        return redirect(url_for('showAll'))


@app.route('/catalog.json')
def RJSON():
    cats = []
    categories = session.query(Category).order_by(asc(Category.categ_id))
    for Categoryl in categories:
        items = session.query(Item).filter_by(categ_id=Categoryl.categ_id).all()
        if items:
            item = []
            cat = OrderedDict([
                ('id', Categoryl.categ_id),
                ('name', Categoryl.name),
                ('item(s)', item)
            ])
            cats.append(cat)
            for i in items:
                itemsl = OrderedDict([
                    ('cat_id', i.categ_id),
                    ('description', i.description),
                    ('id', i.item_id),
                    ('title', i.title)
                ])
                item.append(itemsl)
        else:
            cat = {
                'id': Categoryl.categ_id,
                'name': Categoryl.name
            }
            cats.append(cat)
    r = {'Category': cats}
    return jsonify(r)


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
    url = ('https://www.googleapis.com/oauth2/v1/tokeninfo?access_token=%s'
           % access_token)
    h = httplib2.Http()
    result = json.loads(h.request(url, 'GET')[1])
    # If there was an error in the access token info, abort.
    if result.get('error') is not None:
        response = make_response(json.dumps(result.get('error')), 500)
        response.headers['Content-Type'] = 'application/json'
        return response
    gplus_id = credentials.id_token['sub']
    if result['user_id'] != gplus_id:
        response = make_response(
            json.dumps("Token's user ID doesn't match given user ID."), 401)
        response.headers['Content-Type'] = 'application/json'
        return response
    if result['issued_to'] != CLIENT_ID:
        response = make_response(
            json.dumps("Token's client ID does not match app's."), 401)
        print("Token's client ID does not match app's.")
        response.headers['Content-Type'] = 'application/json'
        return response
    stored_access_token = login_session.get('access_token')
    stored_gplus_id = login_session.get('gplus_id')
    if stored_access_token is not None and gplus_id == stored_gplus_id:
        response = make_response(json.dumps('Current user ' +
                                            'is already connected.'), 200)
        response.headers['Content-Type'] = 'application/json'
        return response
    login_session['access_token'] = credentials.access_token
    login_session['gplus_id'] = gplus_id
    userinfo_url = "https://www.googleapis.com/oauth2/v1/userinfo"
    params = {'access_token': credentials.access_token, 'alt': 'json'}
    answer = requests.get(userinfo_url, params=params)

    data = answer.json()

    login_session['username'] = data['name']
    login_session['provider'] = 'google'
    try:
        u = session.query(customer).filter_by(
            username=login_session['username']).all()
        print(u[0].username)
    except:
        newuser = customer(username=login_session['username'])
        newuser.hash_password('')
        session.add(newuser)
        session.commit()
    flash("you are now logged in as %s" % login_session['username'])
    return 'done'


@app.route('/gdisconnect')
def gdisconnect():
    # Only disconnect a connected user.
    access_token = login_session.get('access_token')
    if access_token is None:
        response = make_response(
            json.dumps('Current user not connected.'), 401)
        response.headers['Content-Type'] = 'application/json'
        return response
    url = 'https://accounts.google.com/o/oauth2/revoke?token=%s' % access_token
    h = httplib2.Http()
    result = h.request(url, 'GET')[0]
    if result['status'] == '200':
        response = make_response(json.dumps('Successfully disconnected.'), 200)
        response.headers['Content-Type'] = 'application/json'
        return response
    else:
        response = make_response(json.dumps('Failed to revoke token ' +
                                            'for given user.', 400))
        response.headers['Content-Type'] = 'application/json'
        return response

if __name__ == '__main__':
    app.secret_key = 'super_secret_key'
    app.debug = True
    app.run(host='0.0.0.0', port=5000)
