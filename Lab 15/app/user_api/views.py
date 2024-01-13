from flask import request
from flask_restful import Resource
from app.profile.models import User
from app import db
from app.user_api.schemas import UserSchema
from . import user_api_bp

class UsersApi(Resource):
    def get(self):
        page = request.args.get('page', 1, type=int)
        per_page = 2
        users_paginator = User.query.paginate(page=page, per_page=per_page)
        users = users_paginator.items
        total_pages = users_paginator.pages
        schema = UserSchema(many=True)
        return {'users': schema.dump(users), 'page': page, 'total_pages': total_pages}

    def post(self):
        schema = UserSchema()
        new_user = schema.load(request.json)
        db.session.add(new_user)
        db.session.commit()
        return {'user': schema.dump(new_user)}, 201

class UserApi(Resource):
    def get(self, id):
        user = User.query.get_or_404(id)
        schema = UserSchema()
        return {"user": schema.dump(user)}

    def put(self, id):
        user = User.query.get_or_404(id)
        schema = UserSchema(partial=True)
        user = schema.load(request.json, instance=user)
        db.session.commit()
        return {"user": schema.dump(user)}

    def delete(self, id):
        user = User.query.get_or_404(id)
        db.session.delete(user)
        db.session.commit()
        return {"message": f"User '{user.username}' deleted"}
