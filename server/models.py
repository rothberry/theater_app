# 📚 Review With Students:
# The dangers of plain text passwords
# What Hashing is
# Hashing vs encryption
# How to Hash a string
# Salting
# Rainbow Tables
# Bcrypt

from ipdb import set_trace
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy_serializer import SerializerMixin
from sqlalchemy.orm import validates
from sqlalchemy.ext.hybrid import hybrid_property

# 3.✅ Import bcrypt from app
# from app import bcrypt


db = SQLAlchemy()


class Production(db.Model, SerializerMixin):
    __tablename__ = 'productions'

    id = db.Column(db.Integer, primary_key=True)

    title = db.Column(db.String, nullable=False)
    genre = db.Column(db.String, nullable=False)
    budget = db.Column(db.Float)
    image = db.Column(db.String)
    director = db.Column(db.String)
    description = db.Column(db.String)
    ongoing = db.Column(db.Boolean, default=True)
    created_at = db.Column(db.DateTime, server_default=db.func.now())
    updated_at = db.Column(db.DateTime, onupdate=db.func.now())
    cast_members = db.relationship('CastMember', backref='production')

    serialize_rules = ('-cast_members.production',)

    @validates('image')
    def validate_image(self, key, image_path):
        if '.jpg' not in image_path:
            raise ValueError("Image file type must be a jpg")
        return image_path

    def __repr__(self):
        return f'<Production Title:{self.title}, Genre:{self.genre}, Budget:{self.budget}, Image:{self.image}, Director:{self.director},ongoing:{self.ongoing}>'


class CastMember(db.Model, SerializerMixin):
    __tablename__ = 'cast_members'

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String)
    role = db.Column(db.String)
    created_at = db.Column(db.DateTime, server_default=db.func.now())
    updated_at = db.Column(db.DateTime, onupdate=db.func.now())
    production_id = db.Column(db.Integer, db.ForeignKey('productions.id'))

    serialize_rules = ('-production.cast_members',)

    def __repr__(self):
        return f'<Production Name:{self.name}, Role:{self.role}'


class User(db.Model, SerializerMixin):
    __tablename__ = 'users'

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String)
    email = db.Column(db.String)
    admin = db.Column(db.String, default=False)
    # # password = db.Column(db.String, nullable=False)
    created_at = db.Column(db.DateTime, server_default=db.func.now())
    updated_at = db.Column(db.DateTime, onupdate=db.func.now())

    """ 
        How should passwords work?

        If we just saved the passwords as strings inot our database, what are the issues?
        - if someone can see the db, then they can see all the passwords

        End goal is to never know the users password on the backend

        Hashing: 1 way process
        - Password + some_secret_key + some algo => new_password
        - encrypting without a way back

        Salting:
        - Adding more characters to our password before / during / after hashing

        Encrypting: 2 way process
        - Password + some_secret_key + some algo => new_password
        - can Decrypt the password if you know the key and algo

    """

    _password_hash = db.Column(db.String)

    serialize_rules = ("-_password_hash","-admin", "-created_at", "-updated_at")
    # 4.✅ Add a column _password_hash
    #   Note: When an underscore is used, it's a sign that the variable or method is for internal use.

    # 5.✅ Create a hybrid_property that will protect the hash from being viewed
    #   The hybrid_propery will assign all the SQLAlchemy attributes to this getter method

    @hybrid_property
    def password_hash(self):
        return self._password_hash

    # 6.✅ Navigate to app

    # 7.✅ Create a setter method called password_hash that takes self and a password.
    #   7.1 Use bcyrpt to generate the password hash with bcrypt.generate_password_hash
    #   7.2 Set the _password_hash to the hashed password

    @password_hash.setter
    def password_hash(self, password):
        # the only time where the password will be the actual string
        from app import bcrypt
        pw_hash = bcrypt.generate_password_hash(password.encode("utf-8"))
        self._password_hash = pw_hash.decode("utf-8")

    # 8.✅ Create an authenticate method that uses bcyrpt to verify the password against the hash in the DB with bcrypt.check_password_hash

    def authenticate(self, password):
        from app import bcrypt
        return bcrypt.check_password_hash(self._password_hash, password.encode("utf-8"))

    # 9.✅ Navigate to app

    def __repr__(self):
        return f'USER: ID: {self.id}, Name {self.name}, Email: {self.email}, Admin: {self.admin}'
