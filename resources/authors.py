from datetime import datetime
from flask import request
from flask_jwt_extended import jwt_required
from flask_restful import Resource

from helpers.pagination_helper import get_paginated_items
from helpers.request_helper import get_entity_or_404
from models import Author as AuthorModel, db
from resources.base_resource import BaseResource
from schemas.author import authors_schema, author_schema
from marshmallow import ValidationError


class Author(Resource):
    @jwt_required()
    def get(self, id):
        author = get_entity_or_404(db.session, AuthorModel, id)
        return author_schema.dump(author)

    @jwt_required()
    def delete(self, id):
        author = get_entity_or_404(db.session, AuthorModel, id)
        db.session.delete(author)
        db.session.commit()
        return '', 204

    @jwt_required()
    def put(self, id):
        data = request.get_json()
        author = get_entity_or_404(db.session, AuthorModel, id)
        try:
            schema_data = author_schema.load(data)
        except ValidationError as e:
            return {'message': 'Validation error', 'errors': e.messages}, 400

        author.first_name = schema_data.get('first_name', author.first_name)
        author.last_name = schema_data.get('last_name', author.last_name)
        author.birth_date = schema_data.get('birth_date', author.birth_date)
        author.biography = schema_data.get('biography', author.biography)
        db.session.commit()
        return author_schema.dump(author), 201


class AuthorsList(BaseResource):
    @jwt_required()
    def get(self):
        args = self.reqparse.parse_args()
        page = args['page']
        per_page = args['per_page']

        authors = get_paginated_items(AuthorModel.query, page, per_page)
        return authors_schema.dump(authors), 200

    @jwt_required()
    def post(self):
        data = request.get_json()
        try:
            schema_data = author_schema.load(data)
        except ValidationError as e:
            return {'message': 'Validation error', 'errors': e.messages}, 400

        new_author = AuthorModel(**schema_data)
        db.session.add(new_author)
        db.session.commit()

        return author_schema.dump(new_author), 201