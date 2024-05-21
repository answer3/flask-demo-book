from flask_jwt_extended import jwt_required

from helpers.pagination_helper import get_paginated_items
from helpers.request_helper import get_entity_or_404
from models import db, Author as AuthorModel, Book as BookModel
from resources.base_resource import BaseResource
from schemas.book import book_list_schema


class AuthorBooks(BaseResource):
    @jwt_required()
    def get(self, id):
        author = get_entity_or_404(db.session, AuthorModel, id)

        args = self.reqparse.parse_args()
        page = args['page']
        per_page = args['per_page']

        books = get_paginated_items(BookModel.query.filter_by(author_id=author.id), page, per_page)
        return book_list_schema.dump(books), 200