from flask import Blueprint

feedback_bp = Blueprint('feedback', __name__, template_folder='templates')

from . import views  # Import the views module to register the routes
