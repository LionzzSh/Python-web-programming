from flask import jsonify, request
from flask_httpauth import HTTPBasicAuth
from sqlalchemy.exc import IntegrityError
from flask_jwt_extended import create_access_token, jwt_required
from werkzeug.security import check_password_hash
from app.profile.views import User
from . import api_bp
from app.todo.models import Todo
from app import db

basic_auth = HTTPBasicAuth()


@basic_auth.verify_password
def authenticate(email, password):
    user = User.query.filter_by(email=email).first()
    if user and user.checkPassword(password):
        return email

@basic_auth.error_handler
def handle_auth_error(status):
    return jsonify(message="Authentication failed"), status

@api_bp.route('/login', methods=['POST'])
@basic_auth.login_required
def perform_login():
    access_token = create_access_token(identity=basic_auth.current_user())
    return jsonify(access_token=access_token)

@api_bp.route('/ping', methods=['GET'])
def ping():
    return jsonify({
        "message": "pong"
    })

@api_bp.route('/todos', methods=['GET'])
@jwt_required()
def get_todos():
    todos = Todo.query.all()

    todo_list = []

    for todo in todos:
        item = {
            "id": todo.id,
            "task": todo.task,
            "status": todo.status
        }

        todo_list.append(item)

    return jsonify(todo_list)

@api_bp.route('/todos', methods=['POST'])
@jwt_required()
def post_todos():
    new_data = request.get_json()

    if not new_data:
        return jsonify({"message": "no input data provided"}), 400

    if not new_data.get('task') or 'status' not in new_data:
        return jsonify({"message": "required fields are missing"}), 422

    todo = Todo(task=new_data.get('task'), status=new_data.get('status'))

    db.session.add(todo)
    db.session.commit()

    new_todo = Todo.query.filter_by(id=todo.id).first()

    return jsonify({
        "id": new_todo.id,
        "task": new_todo.task,
        "status": new_todo.status
    }), 201

@api_bp.route('/todos/<int:id>', methods=['GET'])
@jwt_required()
def get_todo(id):
    todo = Todo.query.filter_by(id=id).first()

    if not todo:
        return jsonify({"message": f"todo with id = {id} not found"}), 404

    return jsonify({
        "id": todo.id,
        "task": todo.task,
        "status": todo.status
    }), 200

@api_bp.route('/todos/<int:id>', methods=['PUT'])
@jwt_required()
def update_todo(id):
    todo = Todo.query.filter_by(id=id).first()

    if not todo:
        return jsonify({"message": f"todo with id = {id} not found"}), 404

    new_data = request.get_json()

    if not new_data:
        return jsonify({"message": "no input data provided"}), 400

    if 'task' in new_data:
        todo.task = new_data['task']

    if 'status' in new_data:
        todo.status = new_data['status']

    try:
        db.session.commit()
    except IntegrityError:
        db.session.rollback()

    return jsonify({
        "message": "todo was updated"
    }), 204

@api_bp.route('/todos/<int:id>', methods=['DELETE'])
@jwt_required()
def delete_todo(id):
    todo = Todo.query.get(id)

    if not todo:
        return jsonify({"message": f"todo with id = {id} not found"}), 404

    db.session.delete(todo)
    db.session.commit()

    return jsonify({"message": "Resource successfully deleted."}), 200
