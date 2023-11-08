from app import db

class Feedback(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    comment = db.Column(db.Text, nullable=False)

    def __init__(self, name, comment):
        self.name = name
        self.comment = comment

class Todo(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(100), nullable=False)
    description = db.Column(db.Text)  # Add the description field
    complete = db.Column(db.Boolean, default=False)

    def __init__(self, title, description=None, complete=False):
        self.title = title
        self.description = description
        self.complete = complete
