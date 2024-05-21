import os
import unittest
from flask_testing import TestCase
from api import init_app
from models import db


class TestAuth(TestCase):
    def create_app(self):
        os.environ['FLASK_ENV'] = 'test'
        app = init_app()
        return app

    def tearDown(self):
        db.session.remove()
        db.drop_all()

    def test_signup_login(self):
        req_data = {"username": "user1", "password": "aaabbbcccddd"}
        response = self.client.post('api/signup', json=req_data)
        self.assertEqual(response.status_code, 201)
        self.assertEqual(response.json, {"message": "User created successfully"})

        response = self.client.post('api/login', json=req_data)
        self.assertEqual(response.status_code, 200)
        self.assertTrue("access_token" in response.json)

    def test_signup_validation(self):
        req_data = {"username": "us", "password": "aa"}
        response = self.client.post('api/signup', json=req_data)
        self.assertEqual(response.json['message'], "Validation error")
        self.assertEqual(response.json['errors']['username'], ["Length must be between 3 and 15."])
        self.assertEqual(response.json['errors']['password'], ["Length must be between 10 and 50."])

    def test_signup_already_exists(self):
        req_data = {"username": "user1", "password": "aaabbbcccddd"}
        response = self.client.post('api/signup', json=req_data)
        self.assertEqual(response.status_code, 201)
        self.assertEqual(response.json, {"message": "User created successfully"})

        response = self.client.post('api/signup', json=req_data)
        self.assertEqual(response.status_code, 400)
        self.assertEqual(response.json, {"message": "Username already exists."})

    def test_login_validation(self):
        req_data = {"username": "user1", "password": "aaabbbcccddd"}
        response = self.client.post('api/signup', json=req_data)
        self.assertEqual(response.status_code, 201)
        self.assertEqual(response.json, {"message": "User created successfully"})

        response = self.client.post('api/login', json={})
        self.assertEqual(response.status_code, 400)
        self.assertEqual(response.json['message'], "Validation error")
        self.assertEqual(response.json['errors']['username'], ["Missing data for required field."])
        self.assertEqual(response.json['errors']['password'], ["Missing data for required field."])

    def test_login_incorrect(self):
        req_data = {"username": "user1", "password": "aaabbbcccddd"}
        response = self.client.post('api/signup', json=req_data)
        self.assertEqual(response.status_code, 201)
        self.assertEqual(response.json, {"message": "User created successfully"})

        req_data = {"username": "user1", "password": "aaabbbcccddd11"}
        response = self.client.post('api/login', json=req_data)
        self.assertEqual(response.status_code, 401)
        self.assertEqual(response.json['message'], "Bad username or password")



