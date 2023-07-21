#!/usr/bin/env python3

from ipdb import set_trace
from dotenv import dotenv_values
from flask import Flask, request, make_response, abort, session, jsonify
from flask_migrate import Migrate

from flask_restful import Api, Resource
from werkzeug.exceptions import NotFound, Unauthorized

from flask_cors import CORS

from flask_bcrypt import Bcrypt
from models import db, Production, CastMember, User
import os

app = Flask(__name__)
CORS(app)
bcrypt = Bcrypt(app)

ENV = dotenv_values("../.env")
app.config['SQLALCHEMY_DATABASE_URI'] = os.environ.get("SQLALCHEMY_DATABASE_URI")
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.json.compact = False

app.secret_key = os.environ.get("SECRET_KEY")

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

class CurrentUser(Resource):
    def get(self):
        try:
            user = User.query.filter_by(id=session["user_id"]).first()
            return make_response(user.to_dict())
        except:
            return make_response({"errors": "Unauthed"}, 401)
api.add_resource(CurrentUser, "/authorized")

class Logout(Resource):
    
    def delete(self):
        session["user_id"] = None
        return make_response("", 204)

api.add_resource(Logout, "/logout")

@app.errorhandler(NotFound)
def handle_not_found(e):
    response = make_response(
        "Not Found: Sorry the resource you are looking for does not exist",
        404
    )
    return response


if __name__ == '__main__':
    app.run(port=5000, debug=True)
