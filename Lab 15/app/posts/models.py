from sqlalchemy import Integer, String, Boolean, TIMESTAMP, ForeignKey
from sqlalchemy.orm import Mapped, mapped_column, relationship
from datetime import datetime
from ..extensions import db
import enum

class EnumTypes(enum.Enum):
    Other = 1
    Pets = 2
    Gym = 3
    Food = 4

post_tag = db.Table(
    'post_tag',
    db.Column('post_id', db.Integer, db.ForeignKey('post.id')),
    db.Column('tag_id', db.Integer, db.ForeignKey('tag.id'))
)


class Post(db.Model):
    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    title: Mapped[str] = mapped_column(String(100))
    text: Mapped[str] = mapped_column(String)
    image: Mapped[str] = mapped_column(String, nullable=True, default="generic_post_pic.jpg")
    created: Mapped[TIMESTAMP] = mapped_column(TIMESTAMP, default=datetime.now())
    type: Mapped[EnumTypes] = mapped_column(db.Enum(EnumTypes), default=EnumTypes.Other.name)
    enabled: Mapped[bool] = mapped_column(Boolean, default=False)
    user_id: Mapped[int] = mapped_column(Integer, ForeignKey('user.id'), nullable=False)  # ForeignKey added
    user = relationship('User', backref='posts')  # Relationship to User added
    category_id: Mapped[int] = mapped_column(Integer, db.ForeignKey('post_category.id', name='fk_category'), nullable=True)
    tags = db.relationship('Tag', secondary=post_tag, backref='posts')

    def __repr__(self) -> str:
        return f"ID:{self.id} Title:{self.title} Created:{self.created} UserID: {self.user_id}"


class PostCategory(db.Model):
    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    name: Mapped[str] = mapped_column(String, nullable=False)
    posts = db.relationship('Post', backref='category')


class Tag(db.Model):
    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    name: Mapped[str] = mapped_column(String, nullable=False)