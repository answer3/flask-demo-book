from flask import request
from flask_restful import Resource
from marshmallow import ValidationError
from flask_jwt_extended import jwt_required, get_jwt_identity

from helpers.pagination_helper import get_paginated_items
from helpers.request_helper import get_entity_or_404
from models import Book as BookModel, db
from resources.base_resource import BaseResource
from schemas.book import book_schema, books_schema


class Book(Resource):
    @jwt_required()
    def get(self, id):
        book = get_entity_or_404(db.session, BookModel, id)
        return book_schema.dump(book)

    @jwt_required()
    def delete(self, id):
        book = get_entity_or_404(db.session, BookModel, id)
        db.session.delete(book)
        db.session.commit()
        return '', 204

    @jwt_required()
    def put(self, id):
        data = request.get_json()
        book = get_entity_or_404(db.session, BookModel, id)
        try:
            schema_data = book_schema.load(data)
        except ValidationError as e:
            return {'message': 'Validation error', 'errors': e.messages}, 400

        book.title = schema_data.get('title', book.title)
        book.isbn = schema_data.get('isbn', book.isbn)
        book.publication_date = schema_data.get('publication_date', book.publication_date)
        book.author_id = schema_data.get('author_id', book.author_id)
        db.session.commit()
        return book_schema.dump(book), 201


class BooksList(BaseResource):
    @jwt_required()
    def get(self):
        args = self.reqparse.parse_args()
        page = args['page']
        per_page = args['per_page']

        books = get_paginated_items(BookModel.query, page, per_page)
        return books_schema.dump(books), 200

    @jwt_required()
    def post(self):
        data = request.get_json()
        try:
            schema_data = book_schema.load(data)
        except ValidationError as e:
            return {'message': 'Validation error', 'errors': e.messages}, 400

        new_book = BookModel(**schema_data)
        db.session.add(new_book)
        db.session.commit()

        return book_schema.dump(new_book), 201