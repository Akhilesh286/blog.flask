# app.py

from flask import Flask, render_template,redirect,request,url_for
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate


app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///users.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

# Initialize SQLAlchemy (don't forget to call db.init_app(app) in the main app file)
db = SQLAlchemy()
db.init_app(app)
migrate = Migrate(app,db)


class Users(db.Model):
    __tablename__ = 'users'
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(50), unique=True, nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    passward = db.Column(db.String(50))

    def __repr__(self):
        return f'<User {self.username}>'

@app.route('/')
def display_users():
    users = Users.query.all()
    return render_template('display.html', users=users,update=False)
