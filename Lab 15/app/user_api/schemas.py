from marshmallow import fields, validate, validates_schema, ValidationError
from app.profile.models import User
from app import ma
from marshmallow_sqlalchemy import SQLAlchemyAutoSchema

class UserSchema(ma.SQLAlchemyAutoSchema):
    username = fields.String(required=True, validate=[validate.Length(min=4, max=10),
                                                      validate.Regexp('^[A-Za-z][a-zA-Z0-9._]+$')])
    email = fields.String(required=True, validate=[validate.Email()])
    password = fields.String(load_only=True, required=True, validate=[validate.Length(min=7)])

    @validates_schema
    def validate_username(self, data, **kwargs):
        username = data.get('username')
        if User.query.filter_by(username=username).count():
            raise ValidationError(f"Username '{username}' already exists")

    @validates_schema
    def validate_email(self, data, **kwargs):
        email = data.get('email')
        if User.query.filter_by(email=email).count():
            raise ValidationError(f"Email '{email}' already exists")

    class Meta:
        model = User
        load_instance = True

    exclude = ('password_hash',)
