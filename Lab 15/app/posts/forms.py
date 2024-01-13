from flask_wtf import FlaskForm
from flask_wtf.file import FileAllowed, FileField
from wtforms import StringField, TextAreaField, BooleanField, SubmitField, SelectField, SelectMultipleField
from wtforms.validators import DataRequired

class PostForm(FlaskForm):
    title = StringField(label='Title', validators=[DataRequired("Title is required")], id="title")
    text = TextAreaField(label='Text', validators=[DataRequired("Text is required")], id="text")
    image = FileField(label='Image', validators=[FileAllowed(['jpg', 'png', 'jpeg', 'gif'])], id="image")
    type = SelectField(label='Post type (select one)', choices=[
        ('Other', "Other"),
        ('Pets', 'Pets'),
        ('Gym', 'Gym'),
        ('Food', 'Food')
    ])
    enabled = BooleanField(label='Show post', id="enabled")
    categories = SelectField('Category', choices=[], coerce=int)  # Make sure categories are added dynamically
    tags = SelectMultipleField('Tags', choices=[], coerce=int)
    submit = SubmitField(label="Save", id="submit")

class CategoryForm(FlaskForm):
    name = StringField(label='Name', validators=[DataRequired("Name is required")])
    submit = SubmitField(label="Save category")

class TagForm(FlaskForm):
    name = StringField(label='Name', validators=[DataRequired("Name is required")])
    submit = SubmitField(label="Save tag")

class SearchForm(FlaskForm):
    category = SelectField(label="Category", coerce=int, choices=[(-1,'all')], default=-1)
    submit = SubmitField(label="Search")