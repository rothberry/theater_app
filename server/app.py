#!/usr/bin/env python3
# 📚 Review With Students:
# Authentication vs Authorization
# Cookies vs Sessions
# How Flask Encrypts Sessions

# Set up:
# cd into server and run the following in the Terminal:
# export FLASK_APP=app.py
# export FLASK_RUN_PORT=5000
# flask db init
# flask db revision --autogenerate -m'Create tables'
# flask db upgrade
# python seed.py
# cd into client and run `npm i`

# Running React together
# In Terminal cd into the root directory, run:
# `honcho start -f Procfile.dev`

""" 
    Both of the Auths

    Authentication:
    - Validating a user to be who they claim
    - Ex: Getting your hand stamped at a bar/club

    Session:
    - Active time while the user is logged into the app
    - a series of activities that the user does
    - Potentinally Encrpyted Object that holds data

    Cookie:
    - Piece of data stored within the browser
    - Mostly used for (and for this lectures purposes) credentials and keeping a user signed in

    Authorization:
    - Level of access that a user can have
    - Ex: Checking the id, make sure you have access
    - This is where the passwords come into play

 """
from ipdb import set_trace
from dotenv import dotenv_values
from flask import Flask, request, make_response, abort, session, jsonify
from flask_migrate import Migrate

from flask_restful import Api, Resource
from werkzeug.exceptions import NotFound, Unauthorized

from flask_cors import CORS

# 1.✅ Import Bcrypt form flask_bcrypt
#   1.1 Invoke Bcrypt and pass it app
from flask_bcrypt import Bcrypt
from models import db, Production, CastMember, User


app = Flask(__name__)
CORS(app)
bcrypt = Bcrypt(app)

app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///app.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.json.compact = False

# Set up:
# generate a secrete key `python -c 'import os; print(os.urandom(16))'`
ENV = dotenv_values("../.env")
app.secret_key = ENV["SECRET_KEY"]

migrate = Migrate(app, db)
db.init_app(app)

api = Api(app)


class Productions(Resource):
    def get(self):
        production_list = [p.to_dict() for p in Production.query.all()]
        response = make_response(
            production_list,
            200,
        )

        return response

    def post(self):
        form_json = request.get_json()
        try:
            new_production = Production(
                title=form_json['title'],
                genre=form_json['genre'],
                budget=int(form_json['budget']),
                image=form_json['image'],
                director=form_json['director'],
                description=form_json['description']
            )
        except ValueError as e:
            abort(422, e.args[0])

        db.session.add(new_production)
        db.session.commit()

        response_dict = new_production.to_dict()

        response = make_response(
            response_dict,
            201,
        )
        return response


api.add_resource(Productions, '/productions')


class ProductionByID(Resource):
    def get(self, id):
        production = Production.query.filter_by(id=id).first()
        if not production:
            abort(404, 'The Production you were looking for was not found')
        production_dict = production.to_dict()
        response = make_response(
            production_dict,
            200
        )

        return response

    def patch(self, id):
        production = Production.query.filter_by(id=id).first()
        if not production:
            abort(404, 'The Production you were trying to update for was not found')

        for attr in request.form:
            setattr(production, attr, request.form[attr])

        production.ongoing = bool(request.form['ongoing'])
        production.budget = int(request.form['budget'])

        db.session.add(production)
        db.session.commit()

        production_dict = production.to_dict()

        response = make_response(
            production_dict,
            200
        )
        return response

    def delete(self, id):
        production = Production.query.filter_by(id=id).first()
        if not production:
            abort(404, 'The Production you were trying to delete was not found')
        db.session.delete(production)
        db.session.commit()

        response = make_response('', 204)

        return response


api.add_resource(ProductionByID, '/productions/<int:id>')

# What are the REST(ish)ful routes for User
# GET       /users      INDEX
# GET       /users/:id  SHOW
# POST      /signup     SIGNUP/REGISTER
# GET       /authorized CURRENT_USER
# POST      /login      LOGIN
# DELETE    /logout     LOGOUT

# 10.✅ Create a Signup route
#   10.1 Use add_resource to add a new endpoint '/signup'
#   10.2 The signup route should have a post method
#       10.2.1 Get the values from the request body with get_json
#       10.2.2 Create a new user, however only pass in the name, email and admin values
#       10.2.3 Call the password_hash method on the new user and set it to the password from the request
#       10.2.4 Add and commit
#       10.2.5 Add the user id to session under the key of user_id
#       10.2.6 send the new user back to the client with a status of 201
#   10.3 Test out your route with the client or Postman


class Signup(Resource):
    def post(self):
        form_json = request.get_json()
        try:
            new_user = User(
                name=form_json["name"],
                email=form_json["email"],
                password_hash=form_json["password"]
            )
            db.session.add(new_user)
            db.session.commit()
            return make_response(new_user.to_dict(), 201)
        except:
            return make_response({"errors": "Bad name / email / password"}, 422)


api.add_resource(Signup, "/signup")
# User.query.order_by(User.id.desc()).first()._password_hash

# 11.✅ Create a Login route
#   11.1 use add add_resource to add the login endpoint
#   11.2 Create a post method
#       11.2.1 Query the user from the DB with the name provided in the request
#       11.2.2 Set the user's id to sessions under the user_id key
#       11.2.3 Create a response to the client with the user's data


class Login(Resource):

    def post(self):
        try:
            user = User.query.filter_by(
                name=request.get_json()["name"]).first()
            if user.authenticate(request.get_json()["password"]):
                session["user_id"] = user.id
                return make_response(user.to_dict())
        except:
            return make_response({"errors": "Invalid Username or Password"}, 401)

api.add_resource(Login, "/login")
# 12 Head to client/components/authenticate


# 13.✅ Create a route that checks to see if the User is currently in sessions
#   13.1 Use add_resource to add an authorized endpoint
#   13.2 Create a Get method
#       13.2.1 Check to see if the user_id is in session
#       13.2.2 If found query the user and send it to the client
#       13.2.3 If not found return a 401 Unauthorized error
class CurrentUser(Resource):
    def get(self):
        try:
            user = User.query.filter_by(id=session["user_id"]).first()
            return make_response(user.to_dict())
        except:
            return make_response({"errors": "Unauthed"}, 401)
api.add_resource(CurrentUser, "/authorized")

# 14.✅ Create a Logout route
#   14.1 Use add_resource to add a logout endpoint
#   14.2 Create a delete method
#       14.2.1 Set the user_id in sessions to None
#       14.2.1 Create a response with no content and a 204
#   14.3 Test out your route with the client or Postman

class Logout(Resource):
    
    def delete(self):
        session["user_id"] = None
        return make_response("", 204)

api.add_resource(Logout, "/logout")
# 14.✅ Navigate to client navigation

@app.errorhandler(NotFound)
def handle_not_found(e):
    response = make_response(
        "Not Found: Sorry the resource you are looking for does not exist",
        404
    )
    return response


if __name__ == '__main__':
    app.run(port=5000, debug=True)
