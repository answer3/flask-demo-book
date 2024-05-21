import os
import pathlib
from datetime import timedelta

from dotenv import load_dotenv
from flask import Flask
from flask_jwt_extended import JWTManager
from flask_restful import Api

from models import db
from resources.author_books import AuthorBooks
from resources.authors import AuthorsList, Author
from resources.books import BooksList, Book
from resources.users import UserSignUp, UserLogin


def init_app():
    app = Flask(__name__)
    api = Api(app, prefix="/api")

    env = os.environ.get('FLASK_ENV', 'dev')
    env_file = f'{os.path.dirname(os.path.abspath(__file__))}/.env.{env}'
    load_dotenv(env_file)

    app.config['SQLALCHEMY_DATABASE_URI'] = os.environ.get('DATABASE_URI')
    db.init_app(app)

    app.config['JWT_SECRET_KEY'] = os.environ.get('JWT_SECRET_KEY')
    app.config['JWT_ACCESS_TOKEN_EXPIRES'] = timedelta(minutes=int(os.environ.get('JWT_ACCESS_TOKEN_EXPIRES_MINUTES')))
    jwt = JWTManager(app)

    with app.app_context():
        db.create_all()

    api.add_resource(UserSignUp, '/signup')
    api.add_resource(UserLogin, '/login')
    api.add_resource(BooksList, '/books')
    api.add_resource(Book, '/books/<id>')
    api.add_resource(AuthorsList, '/authors')
    api.add_resource(Author, '/authors/<id>')
    api.add_resource(AuthorBooks, '/authors/<id>/books')

    return app


if __name__ == '__main__':
    os.environ['FLASK_ENV'] = 'dev'
    app = init_app()
    app.run(debug=True)
