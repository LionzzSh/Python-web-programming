# tests/test_todo.py

import pytest
from flask import url_for
from tests.base_test import BaseTest
from app.todo.models import Todo

class TodoTest(BaseTest):
    # Add this fixture to make 'app' accessible
    @pytest.fixture
    def app(self):
        return self.app

    @pytest.fixture
    def db(self, app):
        from app import db
        with app.app_context():
            db.create_all()
            yield db
            db.session.remove()
            db.drop_all()

    @pytest.fixture
    def client(self, app):
        return app.test_client()

    def register_and_login(self):
        self.client.post(
            url_for('profile.registration'),
            data={'username': 'test_user', 'email': 'test@example.com', 'password': 'test_password', 'confirm_password': 'test_password'},
            follow_redirects=True
        )

        self.client.post(
            url_for('profile.login'),
            data={'email': 'test@example.com', 'password': 'test_password'},
            follow_redirects=True
        )


    @pytest.mark.usefixtures('client', 'db')
    def test_todo_create(self):
        # Define the data for the task
        data = {
            'task': 'Write flask tests',
        }

        # Register a user (create an account)
        self.register_and_login()

        # Use the test client in a context to simulate the request
        with self.client:
            # Send a POST request to create a new todo task
            response = self.client.post(
                url_for('todo.todo'),
                data=data,
                follow_redirects=True
            )

            # Query the database to retrieve the created todo task
            todo = Todo.query.filter_by(task='Write flask tests').first()

            # Print information for debugging
            if todo is not None:
                print(f"Todo ID: {todo.id}, Todo Task: {todo.task}")
            else:
                print("Todo object is None")  # Add this line for debugging

            print(f"Response Status Code: {response.status_code}")
            print(f"Response Data: {response.data.decode('utf-8')}")  # Add this line for debugging

            # Assertions to check if the test passed
            assert response.status_code == 200
            assert todo is not None
            assert todo.task == data['task']

    @pytest.mark.usefixtures('client', 'db')
    def test_update_todo_complete(self):
        todo_1 = Todo(task="todo1", status=False)
        # Access the database session using self.db.session
        self.db.session.add(todo_1)
        self.db.session.commit()

        with self.client:
            response = self.client.post(
                url_for('todo.update_todo', id=todo_1.id),
                follow_redirects=True
            )

            todo = Todo.query.get(todo_1.id)

            if todo is not None:
                print(f"Updated Todo Status: {todo.status}")
            else:
                print("Todo object is None")  # Add this line for debugging

            assert response.status_code == 200
            assert todo is not None
            assert todo.status is True