from flask import Blueprint

todo_bp = Blueprint('todo', __name__, template_folder='templates', static_folder='static')

from . import views
