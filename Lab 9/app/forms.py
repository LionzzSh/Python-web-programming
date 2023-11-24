from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, BooleanField, SubmitField, TextAreaField
from wtforms.validators import DataRequired, Length, Email, ValidationError, Regexp
from app.models import User
from flask_wtf import FlaskForm
from wtforms import StringField, TextAreaField, SubmitField, BooleanField, PasswordField  
from wtforms.validators import DataRequired, Length
from flask_wtf.file import FileField, FileAllowed
from flask_login import current_user

class LoginForm(FlaskForm):
    email = StringField(label='Email', validators=[DataRequired("Це поле обов'язкове"), Email()])
    password = PasswordField(label='Password', validators=[DataRequired("Це поле обов'язкове")])
    remember = BooleanField(label="Запам'ятати мене")
    submit = SubmitField(label="Ввійти")

class RegistrationForm(FlaskForm):
    username = StringField("Username", validators=[DataRequired("Це поле обов'язкове"),
                                                   Length(min=4, max=10),
                                                   Regexp('^[A-Za-z][a-zA-Z0-9._]+$', 0,
                                                          "username must have only "
                                                          "letters, numbers, dots or "
                                                          "underscores")])
    email = StringField(label='Email', validators=[DataRequired("Це поле обов'язкове"), Email()])
    password = PasswordField(label='Password', validators=[DataRequired("Це поле обов'язкове"),
            Length(min=7, message="Mінімум 7 символів")
        ])
    confirm_password = PasswordField(label='Repeat Password', validators=[DataRequired("Це поле обов'язкове")])
    submit = SubmitField(label="Зареєструватись")

    def validate_email(self, field):
        if User.query.filter_by(email=field.data).first():
            raise ValidationError('Email already registered')

    def validate_username(self, field):
        if User.query.filter_by(username=field.data).first():
            raise ValidationError("Username already in use")


class ChangePasswordForm(FlaskForm):
    old_password = PasswordField(label='Old password', validators=[DataRequired("Це поле обов'язкове"),
            Length(min=4, max=10, message="Повинно бути від 4 до 10 символів")])
    new_password = PasswordField(label='New password', validators=[DataRequired("Це поле обов'язкове"),
            Length(min=4, max=10, message="Повинно бути від 4 до 10 символів")])
    submit = SubmitField(label="Зберегти")

class FeedbackForm(FlaskForm):
    name = StringField('Ім’я', validators=[DataRequired()])
    comment = TextAreaField('Коментар', validators=[DataRequired()])
    submit = SubmitField('Надіслати відгук')

class TodoForm(FlaskForm):
    task = StringField('Завдання', validators=[DataRequired()])
    submit = SubmitField('Додати')

    
class UpdateAccountForm(FlaskForm):
    username = StringField("Username", validators=[Length(min=4, max=10),
                                                   Regexp('^[A-Za-z][a-zA-Z0-9._]+$', 0,
                                                          "Username must have only "
                                                          "letters, numbers, dots, or "
                                                          "underscores")])

    email = StringField(label='Email', validators=[Email()])

    image = FileField('Profile Image', validators=[FileAllowed(['jpg', 'png', 'jpeg', 'gif'], 'Images only!')])

    about_me = TextAreaField(label='About Me')

    submit = SubmitField(label="Update")


    def validate_username(self, username):
        if username.data != current_user.username:
            user = User.query.filter_by(username=username.data).first()
            if user:
                raise ValidationError('That username is taken. Please choose a different one.')

    def validate_email(self, email):
        if email.data != current_user.email:
            user = User.query.filter_by(email=email.data).first()
            if user:
                raise ValidationError('That email is taken. Please choose a different one.')
