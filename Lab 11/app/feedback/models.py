from app import db  # Assuming your main app instance is named 'app'
from datetime import datetime

class Feedback(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    comment = db.Column(db.Text, nullable=False)

    def __init__(self, name, comment):
        self.name = name
        self.comment = comment

    def update_last_seen(self):
        self.last_seen = datetime.utcnow()
        db.session.commit()

def __repr__(self):
        return f"<Feedback {self.id}>"