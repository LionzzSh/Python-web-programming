from flask_wtf import FlaskForm
from wtforms import StringField, TextAreaField, SubmitField, BooleanField, PasswordField  # Імпортуємо PasswordField
from wtforms.validators import DataRequired, Length

class FeedbackForm(FlaskForm):
    name = StringField('Name', validators=[DataRequired()])
    comment = TextAreaField('Comment', validators=[DataRequired()])
    submit = SubmitField('Submit Feedback')

class TodoForm(FlaskForm):
    title = StringField('Title', validators=[DataRequired()])
    description = StringField('Description')
    complete = BooleanField('Complete')
    submit = SubmitField('Add Todo')

class LoginForm(FlaskForm):
    username = StringField('Username', validators=[DataRequired()])
    password = PasswordField('Password', validators=[DataRequired(), Length(min=4, max=10)])
    remember = BooleanField('Remember Me')
    submit = SubmitField('Log In')
