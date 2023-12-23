from flask import url_for
from tests import BaseTestCase
from app.profile.models import User
from flask_login import current_user
from flask_login import login_user


class ViewsTest(BaseTestCase):

    # >>>>>>>>>>>>>
    # Resume test starts
    # >>>>>>>>>>>>>

    def test_main_page_loads_successfully(self):
        response = self.client.get(url_for('resume.index'))
        self.assert200(response)
        self.assertIn(b'Vitalii Shmatolokha', response.data)

    def test_skills_page_loads_successfully(self):
        response = self.client.get(url_for('resume.skills'))
        self.assert200(response)
        self.assertIn(b'Programming', response.data)

    def test_biography_page_loads_successfully(self):
        response = self.client.get(url_for('resume.biography'))
        self.assert200(response)
        self.assertIn(b'2004', response.data)
 
    # TEST-END
    # >>>>>>>>>>>>>
    # Profile test starts
    # >>>>>>>>>>>>>

    def test_login_page_loads_successfully(self):
        response = self.client.get(url_for('profile.login'), follow_redirects=True)
        self.assert200(response)
        self.assertIn(b'Email', response.data)

    def test_registration_page_loads_successfully(self):
        response = self.client.get(url_for('profile.registration'), follow_redirects=True)
        self.assert200(response)
        self.assertIn(b'Username', response.data)

    def test_user_registration_success(self):
        response = self.client.post(
            url_for('profile.registration'),
            data={'username': 'test_user', 'email': 'test@example.com', 'password': 'test_password', 'confirm_password': 'test_password'},
            follow_redirects=True
        )
        self.assert200(response)
        registered_user = User.query.filter_by(username='test_user').first()
        self.assertIsInstance(registered_user, User, msg="User should be registered successfully.")

    def test_user_login_and_logout_success(self):
        response = self.client.post(
            url_for('profile.login'),
            data={'email': 'test@example.com', 'password': 'test_password'},
            follow_redirects=True
        )
        self.assert200(response)

        response = self.client.get(url_for('profile.logout'), follow_redirects=True)
        self.assert200(response)

    def test_change_password_success(self):
        self.client.post('/login', data=dict(email='test@example.com', password='test_password'))

        response = self.client.post(
            url_for('profile.change_password'),
            data={'old_password': 'test_password', 'new_password': 'new_test_password'},
            follow_redirects=True
        )

        self.assert200(response)

    def test_users_page_loads_successfully(self):
        response = self.client.get(url_for('profile.users'), follow_redirects=True)
        self.assert200(response)
        self.assertIn(b'Number of users', response.data)




    # TEST-END
    # >>>>>>>>>>>>>
    # todo test starts
    # >>>>>>>>>>>>>
