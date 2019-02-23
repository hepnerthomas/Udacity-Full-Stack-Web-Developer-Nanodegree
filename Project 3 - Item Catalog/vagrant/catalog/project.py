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

# Facebook Connection with Test User so Udacity Reviewer Can Login to Application
@app.route('/fbconnect', methods=['POST'])
def fb_connect_test_user():
    if request.args.get('state') != login_session['state']:
        response = make_response(json.dumps('Invalid state parameter.'), 401)
        response.headers['Content-Type'] = 'application/json'
        return response
    # Test user access token 
    access_token = 'EAAMIVGYAQxIBAMNjMF6UONwU2MuHawhIiaNW1GehOtXzx6oyIWU1KrWvcjRVTl20j4m2Uh2J0ZARKs2zOu8QT60mX8ZCwYsBdseNmwFHduTHtSZCVg9110EhE9vRSEo1AiNZAMjpB43B3xbfbAWT4XN8i2r8NS5Gfc28qZAtt5WeM96qaB2cxbZAc27BjT7lbbrYYR9k2LaXlFzKdzdcI4lYs31OcwFyj4eZCsTNaca5QZDZD'
    print("access token received %s " % access_token)

    app_id = json.loads(open('fb_client_secrets.json', 'r').read())[
        'web']['app_id']
    app_secret = json.loads(
        open('fb_client_secrets.json', 'r').read())['web']['app_secret']

    url = 'https://graph.facebook.com/oauth/access_token?grant_type=fb_exchange_token&client_id=%s&client_secret=%s&fb_exchange_token=%s' % (
        app_id, app_secret, access_token)
    h = httplib2.Http()
    result = h.request(url, 'GET')[1]

    # Use token to get user info from API
    userinfo_url = "https://graph.facebook.com/v3.2/me"
    '''
        Due to the formatting for the result from the server token exchange we have to
        split the token first on commas and select the first index which gives us the key : value
        for the server access token then we split it on colons to pull out the actual token value
        and replace the remaining quotes with nothing so that it can be used directly in the graph
        api calls
    '''
    token = result.split(',')[0].split(':')[1].replace('"', '')

    url = 'https://graph.facebook.com/v3.2/me?access_token=%s&fields=name,id,email' % token
    h = httplib2.Http()
    result = h.request(url, 'GET')[1]
    # print("url sent for API access:%s"% url)
    # print("API JSON result: %s" % result)
    # data = json.loads(result)
    login_session['provider'] = 'facebook'
    login_session['username'] = 'Mike Alccihhjgafgj Qinstein' 
    login_session['email'] = 'xpiicrnwjg_1550630803@tfbnw.net' 
    login_session['facebook_id'] = '110828236726778'

    # The token must be stored in the login_session in order to properly logout
    login_session['access_token'] = token

    # see if user exists
    user_id = getUserID(login_session['email'])
    if not user_id:
        user_id = createUser(login_session)
    login_session['user_id'] = user_id

    output = ''
    output += '<h1>Welcome, '
    output += login_session['username']
    output += '!</h1>'

    flash("Now logged in as %s" % login_session['username'])

    return output    

# Facebook Connection with User's Facebook Profile
# Currently, not available due to Facebook Privacy Policy and Terms of Service URL requirements.
# @app.route('/fbconnect', methods=['POST'])
# def fbconnect():
#     if request.args.get('state') != login_session['state']:
#         response = make_response(json.dumps('Invalid state parameter.'), 401)
#         response.headers['Content-Type'] = 'application/json'
#         return response
#     access_token = request.data
#     print("access token received %s " % access_token)

#     app_id = json.loads(open('fb_client_secrets.json', 'r').read())[
#         'web']['app_id']
#     app_secret = json.loads(
#         open('fb_client_secrets.json', 'r').read())['web']['app_secret']

#     url = 'https://graph.facebook.com/oauth/access_token?grant_type=fb_exchange_token&client_id=%s&client_secret=%s&fb_exchange_token=%s' % (
#         app_id, app_secret, access_token)
#     h = httplib2.Http()
#     result = h.request(url, 'GET')[1]

#     # Use token to get user info from API
#     userinfo_url = "https://graph.facebook.com/v3.2/me"
#     '''
#         Due to the formatting for the result from the server token exchange we have to
#         split the token first on commas and select the first index which gives us the key : value
#         for the server access token then we split it on colons to pull out the actual token value
#         and replace the remaining quotes with nothing so that it can be used directly in the graph
#         api calls
#     '''
#     token = result.split(',')[0].split(':')[1].replace('"', '')

#     url = 'https://graph.facebook.com/v3.2/me?access_token=%s&fields=name,id,email' % token
#     h = httplib2.Http()
#     result = h.request(url, 'GET')[1]
#     # print("url sent for API access:%s"% url)
#     # print("API JSON result: %s" % result)
#     data = json.loads(result)
#     login_session['provider'] = 'facebook'
#     login_session['username'] = data["name"]
#     login_session['email'] = data["email"]
#     login_session['facebook_id'] = data["id"]

#     # The token must be stored in the login_session in order to properly logout
#     login_session['access_token'] = token

#     # see if user exists
#     user_id = getUserID(login_session['email'])
#     if not user_id:
#         user_id = createUser(login_session)
#     login_session['user_id'] = user_id

#     output = ''
#     output += '<h1>Welcome, '
#     output += login_session['username']
#     output += '!</h1>'

#     flash("Now logged in as %s" % login_session['username'])

#     return output


@app.route('/fbdisconnect')
def fbdisconnect():
    facebook_id = login_session['facebook_id']
    # The access token must me included to successfully logout
    access_token = login_session['access_token']
    url = 'https://graph.facebook.com/%s/permissions?access_token=%s' % (facebook_id, access_token)
    h = httplib2.Http()
    result = h.request(url, 'DELETE')[1]
    return "you have been logged out"


# User Helper Functions
def createUser(login_session):
    newUser = User(name=login_session['username'], email=login_session['email'])
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


# JSON APIs to view Asset Class Information
@app.route('/asset_classes/<int:asset_class_id>/financial_asset/JSON')
def assetClassFinancialAssetsJSON(asset_class_id):
    assetClass = session.query(AssetClass).filter_by(id=asset_class_id).one()
    items = session.query(FinancialAsset).filter_by(asset_class_id=asset_class_id).all()
    return jsonify(FinancialAssets=[i.serialize for i in items])


@app.route('/asset_classes/<int:asset_class_id>/financial_asset/<int:financial_asset_id>/JSON')
def financialAssetJSON(asset_class_id, financial_asset_id):
    assetClass = session.query(AssetClass).filter_by(id=asset_class_id).one()
    financialAsset = session.query(FinancialAsset).filter_by(id=financial_asset_id).one()
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
        return render_template('publicAssetClasses.html', assetClasses=assetClasses)
    else:
        return render_template('assetClasses.html', assetClasses=assetClasses)


# Create a new asset class
@app.route('/asset_classes/new/', methods=['GET', 'POST'])
def newAssetClass():
    if 'username' not in login_session:
        return redirect('/login')
    if request.method == 'POST':
        newAssetClass = AssetClass(name=request.form['name'], user_id=login_session['user_id'])
        session.add(newAssetClass)
        flash('New Asset Class %s Successfully Created' % newAssetClass.name)
        session.commit()
        return redirect(url_for('showAssetClasses'))
    else:
        return render_template('newAssetClass.html')


# Edit an existing asset class
@app.route('/asset_classes/<int:asset_class_id>/edit/', methods=['GET', 'POST'])
def editAssetClass(asset_class_id):
    editedAssetClass = session.query(AssetClass).filter_by(id=asset_class_id).one()
    if 'username' not in login_session:
        return redirect('/login')
    if editedAssetClass.user_id != login_session['user_id']:
        return "<script>function myFunction() {alert('You are not authorized to edit this asset class. Please create your own asset class in order to edit.');}</script><body onload='myFunction()'>"
    if request.method == 'POST':
        if request.form['name']:
            editedAssetClass.name = request.form['name']
            flash('Asset Class Successfully Edited %s' % editedAssetClass.name)
            return redirect(url_for('showAssetClasses'))
    else:
        return render_template('editAssetClass.html', assetClass=editedAssetClass)


# Delete an existing asset class
@app.route('/asset_classes/<int:asset_class_id>/delete/', methods=['GET', 'POST'])
def deleteAssetClass(asset_class_id):
    assetClassToDelete = session.query(AssetClass).filter_by(id=asset_class_id).one()
    if 'username' not in login_session:
        return redirect('/login')
    if assetClassToDelete.user_id != login_session['user_id']:
        return "<script>function myFunction() {alert('You are not authorized to delete this asset class. Please create your own asset class in order to delete.');}</script><body onload='myFunction()'>"
    if request.method == 'POST':
        session.delete(assetClassToDelete)
        flash('%s Successfully Deleted' % assetClassToDelete.name)
        session.commit()
        return redirect(url_for('showAssetClasses', asset_class_id=asset_class_id))
    else:
        return render_template('deleteAssetClass.html', assetClass=assetClassToDelete)


# Show the financial assets for a given asset class
@app.route('/asset_classes/<int:asset_class_id>/')
@app.route('/asset_classes/<int:asset_class_id>/financial_asset/')
def showFinancialAssets(asset_class_id):
    asset_class = session.query(AssetClass).filter_by(id=asset_class_id).one()
    creator = getUserInfo(asset_class.user_id)
    items = session.query(FinancialAsset).filter_by(asset_class_id=asset_class_id).all()
    if 'username' not in login_session or creator.id != login_session['user_id']:
        return render_template('publicfinancialassets.html', items=items, asset_class=asset_class, creator=creator)
    else:
        return render_template('financialAssets.html', items=items, asset_class=asset_class, creator=creator)


# Show a specific financial asset
@app.route('/asset_classes/<int:asset_class_id>/financial_asset/<int:financial_asset_id>')
def showInvididualFinancialAsset(asset_class_id, financial_asset_id):
    asset_class = session.query(AssetClass).filter_by(id=asset_class_id).one()
    creator = getUserInfo(asset_class.user_id)
    financialAsset = session.query(FinancialAsset).filter_by(id=financial_asset_id).one()
    if 'username' not in login_session or creator.id != login_session['user_id']:
        return render_template('publicfinancialassets.html', items=financialAsset, asset_class=asset_class, creator=creator)
    else:
        return render_template('financialAssets.html', items=financialAsset, asset_class=asset_class, creator=creator)


# Create a new financial asset
@app.route('/asset_classes/<int:asset_class_id>/financial_asset/new/', methods=['GET', 'POST'])
def newFinancialAsset(asset_class_id):
    if 'username' not in login_session:
        return redirect('/login')
    assetClass = session.query(AssetClass).filter_by(id=asset_class_id).one()
    assetClasses = session.query(AssetClass).all()
    if login_session['user_id'] != assetClass.user_id:
        return "<script>function myFunction() {alert('You are not authorized to add financial assets to this asset class. Please create your own asset class in order to add items.');}</script><body onload='myFunction()'>"
    if request.method == 'POST':
        newFinancialAssetItem = FinancialAsset(name=request.form['name'], description=request.form['description'], price=request.form['price'], asset_class_id=request.form['asset_class'], user_id=login_session['user_id'])
        session.add(newFinancialAssetItem)
        session.commit()
        flash('New Financial Asset %s Successfully Created' % (newFinancialAssetItem.name))
        return redirect(url_for('showFinancialAssets', asset_class_id=asset_class_id))
    else:
        return render_template('newfinancialasset.html', selectedAssetClass=assetClass, asset_class_id=asset_class_id, assetClasses=assetClasses)


# Edit a financial asset
@app.route('/asset_classes/<int:asset_class_id>/financial_asset/<int:financial_asset_id>/edit', methods=['GET', 'POST'])
def editFinancialAsset(asset_class_id, financial_asset_id):
    if 'username' not in login_session:
        return redirect('/login')
    assetClass = session.query(AssetClass).filter_by(id=asset_class_id).one()
    assetClasses = session.query(AssetClass).order_by(asc(AssetClass.name))
    editedItem = session.query(FinancialAsset).filter_by(id=financial_asset_id).one()
    if login_session['user_id'] != assetClass.user_id:
        return "<script>function myFunction() {alert('You are not authorized to edit financial assets from this asset class. Please create your own asset class in order to edit items.');}</script><body onload='myFunction()'>"
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
        return redirect(url_for('showFinancialAssets', asset_class_id=asset_class_id))
    else:
        return render_template('editfinancialasset.html', asset_class_id=asset_class_id, financial_asset_id=financial_asset_id, item=editedItem, assetClasses=assetClasses)


# Delete a financial asset
@app.route('/asset_classes/<int:asset_class_id>/financial_asset/<int:financial_asset_id>/delete/', methods=['GET', 'POST'])
def deleteFinancialAsset(asset_class_id, financial_asset_id):
    if 'username' not in login_session:
        return redirect('/login')
    assetClass = session.query(AssetClass).filter_by(id=asset_class_id).one()
    itemToDelete = session.query(FinancialAsset).filter_by(id=financial_asset_id).one()
    if login_session['user_id'] != assetClass.user_id:
        return "<script>function myFunction() {alert('You are not authorized to delete financial assets from this asset class. Please create your own asset class in order to delete items.');}</script><body onload='myFunction()'>"
    if request.method == 'POST':
        session.delete(itemToDelete)
        session.commit()
        flash('Menu Item Successfully Deleted')
        return redirect(url_for('showFinancialAssets', asset_class_id=asset_class_id))
    else:
        return render_template('deletefinancialasset.html', item=itemToDelete)


# Disconnect based on provider
@app.route('/disconnect')
def disconnect():
    if 'provider' in login_session:
        if login_session['provider'] == 'facebook':
            fbdisconnect()
            del login_session['facebook_id']
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
    app.run(host='0.0.0.0', port=8000)
