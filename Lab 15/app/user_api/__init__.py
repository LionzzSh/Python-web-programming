from flask import Blueprint, jsonify
from flask_restful import Api
from marshmallow import ValidationError

user_api_bp = Blueprint('user_api', __name__)

from .views import UsersApi, UserApi

api = Api(user_api_bp)

api.add_resource(UsersApi, '/users')
api.add_resource(UserApi, '/users/<int:id>')

@user_api_bp.errorhandler(ValidationError)
def handle_validation_error(e):
    return jsonify({"error": str(e)}), 400
