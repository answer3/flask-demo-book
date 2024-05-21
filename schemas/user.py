from marshmallow import Schema, fields, validate, ValidationError, validates
from models import User as UserModel, db


class UserSchema(Schema):
    id = fields.Int()
    username = fields.Str(required=True, validate=validate.Length(min=3, max=15))
    password = fields.Str(required=True, validate=validate.Length(min=10, max=50))


user_schema = UserSchema()
