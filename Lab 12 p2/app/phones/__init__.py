from flask import Blueprint

phones_bp = Blueprint('phones_api', __name__)

from . import views  # Import views module

# Register the Blueprint
from .views import phones_bp
