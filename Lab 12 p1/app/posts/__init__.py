from flask import Blueprint

posts_bp = Blueprint('posts', __name__, template_folder='templates', static_folder='static', static_url_path='posts/static')