#!/usr/bin/env python3
from flask import Flask, render_template, request
from flask import redirect, jsonify, url_for, flash
from sqlalchemy import create_engine, asc
from sqlalchemy.orm import sessionmaker
from database_setup import Base, AssetClass, FinancialAsset, User
from flask import session as login_session
import random
import string
from oauth2client.client import flow_from_clientsecrets
from oauth2client.client import FlowExchangeError
import httplib2
import json
from flask import make_response
import requests


app = Flask(__name__)

CLIENT_ID = json.loads(
    open('client_secrets.json', 'r').read())['web']['client_id']
APPLICATION_NAME = "Financial Asset Application"

# Connect to Database and create database session
engine = create_engine('sqlite:///financialAssetswithusers.db')
Base.metadata.bind = engine

DBSession = sessionmaker(bind=engine)
session = DBSession()


# Create anti-forgery state token
@app.route('/login')
def showLogin():
    state = ''.join(random.choice(string.ascii_uppercase + string.digits)
                    for x in xrange(32))
    login_session['state'] = state
    # return "The current session state is %s" % login_session['state']
    return render_template('login.html', STATE=state)

# Google Connection with User's Google Profile
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
        print("Token's client ID does not match app's.")
        response.headers['Content-Type'] = 'application/json'
        return response

    stored_access_token = login_session.get('access_token')
    stored_gplus_id = login_session.get('gplus_id')
    if stored_access_token is not None and gplus_id == stored_gplus_id:
        message = 'Current user is already connected.'
        response = make_response(json.dumps(message),
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

    # Replace username with email
    # Name is no longer available in the oauth2 API
    login_session['username'] = data['email']
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

    flash("Now logged in as %s" % login_session['username'])

    return output


# User Helper Functions
def createUser(login_session):
    newUser = User(name=login_session['username'],
                   email=login_session['email'])
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
    except AttributeError:
        return None


# JSON APIs to view Asset Class Information
@app.route('/asset_classes/<int:asset_class_id>/financial_asset/JSON')
def assetClassFinancialAssetsJSON(asset_class_id):
    assetClass = session.query(AssetClass) \
        .filter_by(id=asset_class_id).one()
    items = session.query(FinancialAsset) \
        .filter_by(asset_class_id=asset_class_id).all()
    return jsonify(FinancialAssets=[i.serialize for i in items])


@app.route('/asset_classes/<int:asset_class_id>/financial_asset/' +
           '<int:financial_asset_id>/JSON')
def financialAssetJSON(asset_class_id, financial_asset_id):
    assetClass = session.query(AssetClass).filter_by(id=asset_class_id).one()
    financialAsset = session.query(FinancialAsset) \
        .filter_by(id=financial_asset_id).one()
    return jsonify(FinancialAsset=financialAsset.serialize)


@app.route('/asset_classes/JSON')
def assetClassesJSON():
    assetClasses = session.query(AssetClass).all()
    return jsonify(assetClasses=[a.serialize for a in assetClasses])


# Show all financial asset class
@app.route('/')
@app.route('/asset_classes/')
def showAssetClasses():
    assetClasses = session.query(AssetClass).order_by(asc(AssetClass.name))
    if 'username' not in login_session:
        return render_template('publicAssetClasses.html',
                               assetClasses=assetClasses)
    else:
        return render_template('assetClasses.html', assetClasses=assetClasses)


# Create a new asset class
@app.route('/asset_classes/new/', methods=['GET', 'POST'])
def newAssetClass():
    if 'username' not in login_session:
        return redirect('/login')
    if request.method == 'POST':
        newAssetClass = AssetClass(name=request.form['name'],
                                   user_id=login_session['user_id'])
        session.add(newAssetClass)
        flash('New Asset Class %s Successfully Created' % newAssetClass.name)
        session.commit()
        return redirect(url_for('showAssetClasses'))
    else:
        return render_template('newAssetClass.html')


# Edit an existing asset class
@app.route('/asset_classes/<int:asset_class_id>/edit/',
           methods=['GET', 'POST'])
def editAssetClass(asset_class_id):
    editedAssetClass = session.query(AssetClass) \
        .filter_by(id=asset_class_id).one()
    if 'username' not in login_session:
        return redirect('/login')
    if editedAssetClass.user_id != login_session['user_id']:
        return "<script>function myFunction() {alert('You are not " \
               "authorized to edit this asset class. Please create " \
               "your own asset class in order to edit.');}" \
                "</script><body onload='myFunction()'>"
    if request.method == 'POST':
        if request.form['name']:
            editedAssetClass.name = request.form['name']
            flash('Asset Class Successfully Edited %s' % editedAssetClass.name)
            return redirect(url_for('showAssetClasses'))
    else:
        return render_template('editAssetClass.html',
                               assetClass=editedAssetClass)


# Delete an existing asset class
@app.route('/asset_classes/<int:asset_class_id>/delete/',
           methods=['GET', 'POST'])
def deleteAssetClass(asset_class_id):
    assetClassToDelete = session.query(AssetClass) \
        .filter_by(id=asset_class_id).one()
    if 'username' not in login_session:
        return redirect('/login')
    if assetClassToDelete.user_id != login_session['user_id']:
        return "<script>function myFunction() {alert('You are not " \
               "authorized to delete this asset class. Please " \
               "create your own asset class in order to delete.');}" \
               "</script><body onload='myFunction()'>"
    if request.method == 'POST':
        session.delete(assetClassToDelete)
        flash('%s Successfully Deleted' % assetClassToDelete.name)
        session.commit()
        return redirect(url_for('showAssetClasses',
                                asset_class_id=asset_class_id))
    else:
        return render_template('deleteAssetClass.html',
                               assetClass=assetClassToDelete)


# Show the financial assets for a given asset class
@app.route('/asset_classes/<int:asset_class_id>/')
@app.route('/asset_classes/<int:asset_class_id>/financial_asset/')
def showFinancialAssets(asset_class_id):
    asset_class = session.query(AssetClass).filter_by(id=asset_class_id).one()
    creator = getUserInfo(asset_class.user_id)
    items = session.query(FinancialAsset) \
        .filter_by(asset_class_id=asset_class_id).all()
    if 'username' not in login_session or \
            creator.id != login_session['user_id']:
        return render_template('publicfinancialassets.html',
                               items=items,
                               asset_class=asset_class,
                               creator=creator)
    else:
        return render_template('financialAssets.html',
                               items=items,
                               asset_class=asset_class,
                               creator=creator)


# Show a specific financial asset
@app.route('/asset_classes/<int:asset_class_id>/financial_asset/' +
           '<int:financial_asset_id>/')
def showInvididualFinancialAsset(asset_class_id, financial_asset_id):
    asset_class = session.query(AssetClass).filter_by(id=asset_class_id).one()
    creator = getUserInfo(asset_class.user_id)
    financialAsset = session.query(FinancialAsset) \
        .filter_by(id=financial_asset_id).all()
    if 'username' not in login_session \
            or creator.id != login_session['user_id']:
        return render_template('publicfinancialassets.html',
                               items=financialAsset,
                               asset_class=asset_class,
                               creator=creator)
    else:
        return render_template('financialAssets.html',
                               items=financialAsset,
                               asset_class=asset_class,
                               creator=creator)


# Create a new financial asset
@app.route('/asset_classes/<int:asset_class_id>/financial_asset/new/',
           methods=['GET', 'POST'])
def newFinancialAsset(asset_class_id):
    if 'username' not in login_session:
        return redirect('/login')
    assetClass = session.query(AssetClass).filter_by(id=asset_class_id).one()
    assetClasses = session.query(AssetClass).all()
    if login_session['user_id'] != assetClass.user_id:
        return "<script>function myFunction() {alert('You are not " \
               "authorized to add financial assets to this asset " \
               "class. Please create your own asset class in order " \
               "to add items.');}</script><body onload='myFunction()'>"
    if request.method == 'POST':
        newFinancialAssetItem = FinancialAsset(
                                    name=request.form['name'],
                                    description=request.form['description'],
                                    price=request.form['price'],
                                    asset_class_id=request.form['asset_class'],
                                    user_id=login_session['user_id'])
        session.add(newFinancialAssetItem)
        session.commit()
        flash('New Financial Asset %s Successfully Created'
              % (newFinancialAssetItem.name))
        return redirect(url_for('showFinancialAssets',
                                asset_class_id=asset_class_id))
    else:
        return render_template('newfinancialasset.html',
                               selectedAssetClass=assetClass,
                               asset_class_id=asset_class_id,
                               assetClasses=assetClasses)


# Edit a financial asset
@app.route('/asset_classes/<int:asset_class_id>/financial_asset/' +
           '<int:financial_asset_id>/edit',
           methods=['GET', 'POST'])
def editFinancialAsset(asset_class_id, financial_asset_id):
    if 'username' not in login_session:
        return redirect('/login')
    assetClass = session.query(AssetClass).filter_by(id=asset_class_id).one()
    assetClasses = session.query(AssetClass).order_by(asc(AssetClass.name))
    editedItem = session.query(FinancialAsset) \
        .filter_by(id=financial_asset_id).one()
    if login_session['user_id'] != assetClass.user_id:
        return "<script>function myFunction() {alert('You are not " \
               "authorized to edit financial assets from this asset " \
               "class. Please create your own asset class in order to " \
               "edit items.');}</script><body onload='myFunction()'>"
    if request.method == 'POST':
        print(request.form.keys())
        if request.form['name']:
            editedItem.name = request.form['name']
        if request.form['description']:
            editedItem.description = request.form['description']
        if request.form['price']:
            editedItem.price = request.form['price']
        if request.form['asset_class']:
            editedItem.asset_class_id = request.form['asset_class']

        session.add(editedItem)
        session.commit()
        flash('Financial Asset Successfully Edited')
        return redirect(url_for('showFinancialAssets',
                                asset_class_id=asset_class_id))
    else:
        return render_template('editfinancialasset.html',
                               asset_class_id=asset_class_id,
                               financial_asset_id=financial_asset_id,
                               item=editedItem,
                               assetClasses=assetClasses)


# Delete a financial asset
@app.route('/asset_classes/<int:asset_class_id>/financial_asset/' +
           '<int:financial_asset_id>/delete/',
           methods=['GET', 'POST'])
def deleteFinancialAsset(asset_class_id, financial_asset_id):
    if 'username' not in login_session:
        return redirect('/login')
    assetClass = session.query(AssetClass).filter_by(id=asset_class_id).one()
    itemToDelete = session.query(FinancialAsset) \
        .filter_by(id=financial_asset_id).one()
    if login_session['user_id'] != assetClass.user_id:
        return "<script>function myFunction() {alert('You are not" \
               "authorized to delete financial assets from this asset " \
               "class. Please create your own asset class in order to " \
               "delete items.');}</script><body onload='myFunction()'>"
    if request.method == 'POST':
        session.delete(itemToDelete)
        session.commit()
        flash('Menu Item Successfully Deleted')
        return redirect(url_for('showFinancialAssets',
                                asset_class_id=asset_class_id))
    else:
        return render_template('deletefinancialasset.html',
                               item=itemToDelete)


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
        message = 'Failed to revoke token for given user.'
        response = make_response(json.dumps(message, 400))
        response.headers['Content-Type'] = 'application/json'
        return response

# Disconnect based on provider
@app.route('/disconnect')
def disconnect():
    if 'provider' in login_session:
        if login_session['provider'] == 'google':
            gdisconnect()
            del login_session['gplus_id']
        del login_session['username']
        del login_session['email']
        del login_session['user_id']
        del login_session['provider']
        flash("You have successfully been logged out.")
        return redirect(url_for('showAssetClasses'))
    else:
        flash("You were not logged in")
        return redirect(url_for('showAssetClasses'))


if __name__ == '__main__':
    app.secret_key = 'super_secret_key'
    app.debug = True
    app.run(host='0.0.0.0', port=8000, threaded=True)
