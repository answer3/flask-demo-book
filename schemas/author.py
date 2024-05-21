from marshmallow import Schema, fields


class AuthorSchema(Schema):
    id = fields.Int()
    first_name = fields.Str(required=True)
    last_name = fields.Str(required=True)
    birth_date = fields.Date(required=False)
    biography = fields.Str(required=False)


author_schema = AuthorSchema()
authors_schema = AuthorSchema(many=True)