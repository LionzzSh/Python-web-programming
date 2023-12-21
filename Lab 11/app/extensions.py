from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from flask_login import LoginManager
from flask_jwt_extended import JWTManager  # Import the correct JWTManager
from jose import jwt as jose_jwt  # Import jwt from jose

db = SQLAlchemy()
migrate = Migrate()
login_manager = LoginManager()
jwt = JWTManager()  # Use JWTManager from flask_jwt_extended
