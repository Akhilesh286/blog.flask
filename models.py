# models.py

from flask_sqlalchemy import SQLAlchemy
from flask_login import UserMixin
from datetime import datetime

db = SQLAlchemy()


class User(db.Model,UserMixin):
    __tablename__ = 'user'  # Specify the table name explicitly
    id = db.Column(db.Integer, primary_key=True)  # Primary key column
    username = db.Column(db.String(80), nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password = db.Column(db.String(120), nullable=False)

    profile = db.relationship('Profile', back_populates='user', uselist=False)
    posts = db.relationship('Post', back_populates='user', lazy=True)

class Post(db.Model):
    __tablename__ = 'posts'  # Specify the table name explicitly
    id = db.Column(db.Integer, primary_key=True)  # Primary key column
    title = db.Column(db.String(50),nullable=False)
    description = db.Column(db.String(200))
    content = db.Column(db.Text, nullable=False)  # For long text
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, onupdate=datetime.utcnow)
    # Foreign key column pointing to the User table
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'))
    user = db.relationship('User', back_populates='posts')

class Profile(db.Model):
    __tablename__ = 'profiles'  # Specify the table name explicitly
    id = db.Column(db.Integer, primary_key=True)  # Primary key column
    firstname = db.Column(db.String(50),nullable=False)
    lastname = db.Column(db.String(50), nullable=True)
    gender = db.Column(db.String(10),default="human")
    bio = db.Column(db.Text, nullable=True)  # For long text
    phone = db.Column(db.Integer, nullable=True)  # Primary key column
    website = db.Column(db.String(200), nullable=True)
    pic = db.Column(db.String(), nullable=True)
    # Foreign key column pointing to the User table
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'))
    user = db.relationship('User', back_populates='profile')
