import unittest
from flask_testing import TestCase
from src.main import create_app
from src.models import db
from src.models.user import User

class AuthTest(TestCase):
    SQLALCHEMY_DATABASE_URI = 'sqlite:///:memory:'
    TESTING = True

    def create_app(self):
        app = create_app()
        app.config['SQLALCHEMY_DATABASE_URI'] = self.SQLALCHEMY_DATABASE_URI
        app.config['TESTING'] = True
        return app

    def setUp(self):
        db.create_all()
        user = User(email='test@example.com', name='Test User')
        user.set_password('Password123')
        db.session.add(user)
        db.session.commit()

    def tearDown(self):
        db.session.remove()
        db.drop_all()

    def test_login_success(self):
        response = self.client.post('/api/auth/login', json={
            'email': 'test@example.com',
            'password': 'Password123'
        })
        self.assertEqual(response.status_code, 200)
        data = response.json
        self.assertIn('access_token', data)
        self.assertIn('refresh_token', data)

    def test_login_fail(self):
        response = self.client.post('/api/auth/login', json={
            'email': 'test@example.com',
            'password': 'WrongPassword'
        })
        self.assertEqual(response.status_code, 401)

    def test_refresh(self):
        login = self.client.post('/api/auth/login', json={
            'email': 'test@example.com',
            'password': 'Password123'
        })
        refresh_token = login.json['refresh_token']
        response = self.client.post('/api/auth/refresh',
            headers={'Authorization': f'Bearer {refresh_token}'})
        self.assertEqual(response.status_code, 200)
        data = response.json
        self.assertIn('access_token', data)
