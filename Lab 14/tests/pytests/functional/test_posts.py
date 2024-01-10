from flask import url_for
from flask_login import current_user
from app.profile.models import User
from app.posts.models import Post
from app import db



def test_get_all_posts(log_in_default_user, init_database):
    number_of_todos = Post.query.count()
    assert number_of_todos == 2

def test_delete_post(client, log_in_default_user, init_database):
    response = client.get(
        url_for('posts.delete_post', id=2),
        follow_redirects=True
    )

    post = Post.query.filter_by(id=2).first()

    assert response.status_code == 200
    assert post is None
    assert b'Post(2) deleted!' in response.data