import platform
from flask import Flask, request, jsonify
from datetime import datetime, timedelta
from config import config
from .extensions import db, migrate, login_manager, jwt, ma
from jose import jwt as jose_jwt
from flask_jwt_extended import JWTManager, jwt_required, create_access_token, get_jwt_identity


def utility_processor():
    os_info = platform.platform()
    user_agent = request.headers.get('User-Agent')
    current_time = datetime.now()
    return {
        'os_info': os_info,
        'user_agent': user_agent,
        'current_time': current_time
    }

def create_app(config_name='DEF'):
    app = Flask(__name__)
    app.config.from_object(config.get(config_name))

    # Initialize extensions
    db.init_app(app)
    migrate.init_app(app, db)
    login_manager.init_app(app)
    jwt.init_app(app)
    ma.init_app(app)

    # Configure login_manager
    login_manager.login_view = 'profile.login'
    login_manager.login_message_category = 'cookies.info'

    # Register the utility_processor function as a context processor
    app.context_processor(utility_processor)

    # Configure JWT
    app.config['JWT_SECRET_KEY'] = 'your_secret_key'  # Change this to your actual secret key
    app.config['JWT_ACCESS_TOKEN_EXPIRES'] = timedelta(days=1)  # Set the expiration time

    # Routes with authentication
    @app.route('/protected', methods=['GET'])
    @jwt_required()
    def protected():
        # Example protected route that requires JWT authentication
        current_user = get_jwt_identity()
        return jsonify(logged_in_as=current_user), 200

    with app.app_context():
        from app.resume.views import resume_bp
        from app.cookies.views import cookies_bp
        from app.profile.views import profile_bp
        from app.todo.views import todo_bp
        from app.feedback.views import feedback_bp
        from app.api.views import api_bp
        from app.phones.views import phones_bp
        from app.posts.views import posts_bp
        from app.user_api.views import user_api_bp
        from app.swagger import swagger_bp

        app.register_blueprint(resume_bp, url_prefix='/')
        app.register_blueprint(cookies_bp, url_prefix='/cookies')
        app.register_blueprint(profile_bp, url_prefix='/profile')
        app.register_blueprint(todo_bp, url_prefix='/todo')
        app.register_blueprint(feedback_bp, url_prefix='/feedback')
        app.register_blueprint(api_bp, url_prefix='/api')
        app.register_blueprint(phones_bp, url_prefix='/phones_api')
        app.register_blueprint(posts_bp, url_prefix='/posts')
        app.register_blueprint(user_api_bp, url_prefix='/user_api/')
        app.register_blueprint(swagger_bp, url_prefix='/swagger')

    return app
