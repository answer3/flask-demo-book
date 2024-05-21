from marshmallow import Schema, fields, validate, ValidationError, validates
from models import Author as AuthorModel, db
from schemas.author import AuthorSchema


class BookListSchema(Schema):
    id = fields.Int()
    title = fields.Str(required=True)
    isbn = fields.Str(required=True, validate=validate.Length(min=10, max=13))
    publication_date = fields.Date(required=True)


class BookSchema(BookListSchema):
    author = fields.Nested(AuthorSchema(only=("id", "first_name", "last_name",)), dump_only=True)
    author_id = fields.Int(required=True, load_only=True)

    @validates("author_id")
    def validate_author_id(self, value):
        author = db.session.get(AuthorModel, value)
        if not author:
            raise ValidationError('Author id {} does not exist.'.format(value))


book_schema = BookSchema()
book_request_schema = BookSchema()
book_list_schema = BookListSchema(many=True)
books_schema = BookSchema(many=True)