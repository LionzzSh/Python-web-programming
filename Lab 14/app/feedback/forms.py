from flask_wtf import FlaskForm
from wtforms import StringField, TextAreaField, SubmitField
from wtforms.validators import DataRequired

class FeedbackForm(FlaskForm):
    name = StringField('Ім’я', validators=[DataRequired()])
    comment = TextAreaField('Коментар', validators=[DataRequired()])
    submit = SubmitField('Надіслати відгук')
