from flask import url_for
from flask_login import current_user
from app import db
from app.profile.models import User
from app.posts.models import Post


def test_all_posts_page_loads(client, log_in_default_user, init_database):
    response = client.get(url_for('posts.posts_page'))
    assert response.status_code == 200
    assert b'Posts List' in response.data


def test_post_create_page_loads(client, log_in_default_user, init_database):
    response = client.get(url_for('posts.add_post'))
    assert response.status_code == 200
    assert b'Create New Post' in response.data


def test_post_by_id_page_loads(client, log_in_default_user, init_database):
    response = client.get(url_for('posts.post_page', id=1))
    assert response.status_code == 200
    assert b'Author' in response.data


def test_post_edit_page_loads(client, log_in_default_user, init_database):
    response = client.get(url_for('posts.update_post', id=1))
    assert response.status_code == 200
    assert b'Change post Content' in response.data