# tests/base_test.py

import unittest
from app import create_app, db, todo  # Update 'app' to the new name of your main application

class BaseTest(unittest.TestCase):
    def setUp(self):
        self.app = create_app('TEST')
        self.app_context = self.app.app_context()
        self.app_context.push()
        db.create_all()

    def tearDown(self):
        db.session.remove()
        db.drop_all()
        self.app_context.pop()
