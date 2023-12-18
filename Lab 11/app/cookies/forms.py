from flask_wtf import FlaskForm
from wtforms import StringField, IntegerField, PasswordField, SubmitField
from wtforms.validators import DataRequired, Length

class ChangePasswordForm(FlaskForm):
    old_password = PasswordField(label='Old password', validators=[DataRequired("Це поле обов'язкове"),
            Length(min=4, max=10, message="Повинно бути від 4 до 10 символів")])
    new_password = PasswordField(label='New password', validators=[DataRequired("Це поле обов'язкове"),
            Length(min=4, max=10, message="Повинно бути від 4 до 10 символів")])
    submit = SubmitField(label="Зберегти")
