from flask import request, jsonify
from flask_restful import Resource
from flask_jwt_extended import create_access_token
from marshmallow import ValidationError
from werkzeug.security import generate_password_hash, check_password_hash
from models import User as UserModel, db
from schemas.user import user_schema


class UserSignUp(Resource):

    def post(self):
        data = request.get_json()
        username = data.get('username')
        password = data.get('password')

        try:
            schema_data = user_schema.load(data)
        except ValidationError as e:
            return {'message': 'Validation error', 'errors': e.messages}, 400

        if UserModel.query.filter_by(username=username).first():
            return {"message": "Username already exists."}, 400

        hashed_password = generate_password_hash(password)
        new_user = UserModel(username=username, password=hashed_password)
        db.session.add(new_user)
        db.session.commit()

        return {"message": "User created successfully"}, 201


class UserLogin(Resource):

    def post(self):
        data = request.get_json()
        username = data.get('username')
        password = data.get('password')

        try:
            schema_data = user_schema.load(data)
        except ValidationError as e:
            return {'message': 'Validation error', 'errors': e.messages}, 400

        user = UserModel.query.filter_by(username=username).first()
        if not user or not check_password_hash(user.password, password):
            return {"message": "Bad username or password"}, 401

        access_token = create_access_token(identity=username)
        return {"access_token": access_token}, 200