import pytest
from flask import url_for
from app import create_app, db
from app.profile.models import User
from app.posts.models import Post

@pytest.fixture(scope='module')
def client():
    app = create_app(config_name='TEST')
    app.config['SERVER_NAME'] = '127.0.0.1:5000'

    with app.test_client() as client:
        with app.app_context():
            db.create_all()
            yield client
            db.session.remove()
            db.drop_all()

@pytest.fixture()
def user_test():
    user = User(username='brand_new', email='brand_new@email.com', password='password')
    return user

@pytest.fixture(scope='module')
def init_database(client):
    # Check if the user already exists
    existing_user = User.query.filter_by(email='patkennedy24@gmail.com').first()
    if not existing_user:
        # Insert user data
        default_user = User(username='patkennedy', email='patkennedy24@gmail.com', password='FlaskIsAwesome')
        post_1 = Post(title="Um consequatur volupta", text='Qui deleniti voluptas', user_id=1)
        post_2 = Post(title="Optio eum rerum", text='Cumque qui omnis voluptatem.', user_id=1)
        db.session.add(default_user)
        db.session.add(post_1)
        db.session.add(post_2)

        # Commit the changes for the users
        db.session.commit()

    yield  # this is where the testing happens!

@pytest.fixture(scope='function')
def log_in_default_user(client):
    user = User.query.filter_by(email='patkennedy24@gmail.com').first()
    if not user:
        pytest.fail("User not found. Make sure the user is created in the 'init_database' fixture.")

    client.post(
        url_for('profile.login'),
        data=dict(email=user.email, password='FlaskIsAwesome'),
        follow_redirects=True
    )

    yield  # this is where the testing happens!

    client.get(url_for('profile.logout'))