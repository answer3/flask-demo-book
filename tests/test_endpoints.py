import datetime
import os
import unittest
from flask_testing import TestCase
from werkzeug.security import generate_password_hash
from flask_jwt_extended import create_access_token

from api import init_app
from models import Author, Book, User, db


class TestEndpoints(TestCase):
    def create_app(self):
        os.environ['FLASK_ENV'] = 'test'
        app = init_app()
        return app

    def setUp(self):
        author1 = Author(
            first_name='Author1',
            last_name='Surname1',
            birth_date=datetime.date(1960, 1, 1),
            biography="About 1")
        author2 = Author(
            first_name='Author2',
            last_name='Surname2',
            birth_date=datetime.date(1965, 5, 5),
            biography="About 2")
        db.session.add_all([author1, author2])
        db.session.commit()

        book1 = Book(
            title='Book 1',
            author_id=author1.id,
            isbn="a1a1a1a1a1a",
            publication_date=datetime.date(2020, 3, 3)
        )
        book2 = Book(
            title='Book 2',
            author_id=author2.id,
            isbn="a1a1a1a1a1b",
            publication_date=datetime.date(2020, 6, 6)
        )

        db.session.add_all([book1, book2])
        db.session.commit()

        username = "user1"
        password = 'passwordpassword'
        hashed_password = generate_password_hash(password)
        new_user = User(username=username, password=hashed_password)
        db.session.add(new_user)
        db.session.commit()

        db.session.close()

        self.access_token = create_access_token(identity=username)
        self.headers = {
            'Authorization': f'Bearer {self.access_token}'
        }

    def tearDown(self):
        db.session.remove()
        db.drop_all()

    # Author endpoints
    def test_get_all_authors(self):
        response = self.client.get('api/authors', headers=self.headers)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(response.json), 2)
        self.assertListEqual(response.json, [
            {'id': 1, 'first_name': 'Author1', "last_name": "Surname1", "birth_date": "1960-01-01",
             "biography": "About 1"},
            {'id': 2, 'first_name': 'Author2', "last_name": "Surname2", "birth_date": "1965-05-05",
             "biography": "About 2"},
        ])

    def test_get_one_author(self):
        response = self.client.get('api/authors/1', headers=self.headers)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json,
                         {'id': 1, 'first_name': 'Author1', "last_name": "Surname1", "birth_date": "1960-01-01",
                          "biography": "About 1"},
                         )

    def test_get_nonexist_author(self):
        response = self.client.get('api/authors/444', headers=self.headers)
        self.assertEqual(response.status_code, 404)

    def test_get_all_authors_pagination(self):
        response = self.client.get('api/authors?per_page=1&page=2', headers=self.headers)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(response.json), 1)
        self.assertListEqual(response.json, [
            {'id': 2, 'first_name': 'Author2', "last_name": "Surname2", "birth_date": "1965-05-05",
             "biography": "About 2"},
        ])

    def test_add_change_delete_new_author(self):
        data = {'first_name': 'Author3', "last_name": "Surname3", "birth_date": "1970-01-01", "biography": "About 3"}
        response = self.client.post('api/authors', json=data, headers=self.headers)
        self.assertEqual(response.status_code, 201)
        self.assertEqual(response.json, {'id': 3, **data})

        response = self.client.get('api/authors', headers=self.headers)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(response.json), 3)

        new_data = {'first_name': 'Author new', "last_name": "Surname new", "birth_date": "1970-01-02",
                    "biography": "About..."}
        response = self.client.put('api/authors/3', json=new_data, headers=self.headers)
        self.assertEqual(response.status_code, 201)
        self.assertEqual(response.json, {'id': 3, **new_data})

        response = self.client.delete('api/authors/3', headers=self.headers)
        self.assertEqual(response.status_code, 204)

        response = self.client.get('api/authors', headers=self.headers)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(response.json), 2)

    def test_add_author_validation(self):
        data = {}
        response = self.client.post('api/authors', json=data, headers=self.headers)
        self.assertEqual(response.status_code, 400)
        self.assertEqual(response.json['message'], "Validation error")
        self.assertEqual(response.json['errors']['first_name'], ["Missing data for required field."])
        self.assertEqual(response.json['errors']['last_name'], ["Missing data for required field."])

    def test_update_author_validation(self):
        data = {}
        response = self.client.put('api/authors/1', json=data, headers=self.headers)
        self.assertEqual(response.status_code, 400)
        self.assertEqual(response.json['message'], "Validation error")
        self.assertEqual(response.json['errors']['first_name'], ["Missing data for required field."])
        self.assertEqual(response.json['errors']['last_name'], ["Missing data for required field."])

    # Books endpoints
    def test_get_all_books(self):
        response = self.client.get('api/books', headers=self.headers)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(response.json), 2)
        self.assertEqual(response.json, [
            {'id': 1, 'title': 'Book 1', 'isbn': "a1a1a1a1a1a", 'publication_date': "2020-03-03",
             "author": {'id': 1, 'first_name': 'Author1', "last_name": "Surname1"}
             },
            {'id': 2, 'title': 'Book 2', 'isbn': "a1a1a1a1a1b", 'publication_date': "2020-06-06",
             "author": {'id': 2, 'first_name': 'Author2', "last_name": "Surname2"}
             }
        ])

    def test_get_one_book(self):
        response = self.client.get('api/books/1', headers=self.headers)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json,
                         {'id': 1, 'title': 'Book 1', 'isbn': "a1a1a1a1a1a", 'publication_date': "2020-03-03",
                          "author": {'id': 1, 'first_name': 'Author1', "last_name": "Surname1"}
                          })

    def test_get_nonexist_book(self):
        response = self.client.get('api/books/444', headers=self.headers)
        self.assertEqual(response.status_code, 404)

    def test_get_all_books_pagination(self):
        response = self.client.get('api/books?per_page=1&page=2', headers=self.headers)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(response.json), 1)
        self.assertListEqual(response.json, [
            {'id': 2, 'title': 'Book 2', 'isbn': "a1a1a1a1a1b", 'publication_date': "2020-06-06",
             "author": {'id': 2, 'first_name': 'Author2', "last_name": "Surname2"}
             }
        ])

    def test_add_change_delete_new_book(self):
        data = {'title': 'Book 3', 'isbn': "a1a1a1a1a1c", 'publication_date': "2021-06-06", "author_id": 1}
        response = self.client.post('api/books', json=data, headers=self.headers)
        self.assertEqual(response.status_code, 201)
        self.assertEqual(response.json, {'id': 3, 'title': 'Book 3', 'isbn': "a1a1a1a1a1c", 'publication_date': "2021-06-06", "author": {'id': 1, 'first_name': 'Author1', "last_name": "Surname1"}})

        response = self.client.get('api/books', headers=self.headers)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(response.json), 3)

        new_data = {'title': 'Book new', 'isbn': "a1a1a1a1a1s", 'publication_date': "2024-06-06", "author_id": 1}

        response = self.client.put('api/books/3', json=new_data, headers=self.headers)
        self.assertEqual(response.status_code, 201)
        self.assertEqual(response.json, {'id': 3, 'title': 'Book new', 'isbn': "a1a1a1a1a1s", 'publication_date': "2024-06-06", "author": {'id': 1, 'first_name': 'Author1', "last_name": "Surname1"}})

        response = self.client.delete('api/books/3', headers=self.headers)
        self.assertEqual(response.status_code, 204)

        response = self.client.get('api/books', headers=self.headers)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(response.json), 2)

    def test_add_book_validation(self):
        data = {'author_id': 222}
        response = self.client.post('api/books', json=data, headers=self.headers)
        self.assertEqual(response.status_code, 400)
        self.assertEqual(response.json['message'], "Validation error")
        self.assertEqual(response.json['errors']['title'], ["Missing data for required field."])
        self.assertEqual(response.json['errors']['isbn'], ["Missing data for required field."])
        self.assertEqual(response.json['errors']['publication_date'], ["Missing data for required field."])
        self.assertEqual(response.json['errors']['author_id'], ["Author id 222 does not exist."])

    def test_update_book_validation(self):
        data = {'author_id': 222}
        response = self.client.put('api/books/1', json=data, headers=self.headers)
        self.assertEqual(response.status_code, 400)
        self.assertEqual(response.json['message'], "Validation error")
        self.assertEqual(response.json['errors']['title'], ["Missing data for required field."])
        self.assertEqual(response.json['errors']['isbn'], ["Missing data for required field."])
        self.assertEqual(response.json['errors']['publication_date'], ["Missing data for required field."])
        self.assertEqual(response.json['errors']['author_id'], ["Author id 222 does not exist."])

    def test_get_author_books(self):
        response = self.client.get('api/authors/1/books', headers=self.headers)
        self.assertEqual(response.status_code, 200)
        self.assertListEqual(response.json, [
            {'id': 1, 'title': 'Book 1', 'isbn': "a1a1a1a1a1a", 'publication_date': "2020-03-03",}
        ])