from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from flask_login import LoginManager

# Extensions
db = SQLAlchemy()
migrate = Migrate()
login_manager = LoginManager()
