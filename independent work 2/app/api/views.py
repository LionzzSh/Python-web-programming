from flask import jsonify, request
from sqlalchemy.exc import IntegrityError
from . import api_bp
from app.todo.models import Todo
from app import db

@api_bp.route('/ban', methods=['GET'])
def ping():
    return jsonify({
        "message": "you get banned"
    })

@api_bp.route('/todos', methods=['GET'])
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
def delete_todo(id):
    todo = Todo.query.get(id)

    if not todo:
        return jsonify({"message": f"todo with id = {id} not found"}), 404

    db.session.delete(todo)
    db.session.commit()

    return jsonify({"message": "Resource successfully deleted."}), 200
