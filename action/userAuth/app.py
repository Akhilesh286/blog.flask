# app.py

from flask import Flask, render_template,redirect,request,url_for
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from flask_bcrypt import Bcrypt
from flask_login import LoginManager,UserMixin,login_user,logout_user,current_user,login_required

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///users.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.secret_key = 'hidden gem'
db = SQLAlchemy()
db.init_app(app)
migrate = Migrate(app,db)

login_manager = LoginManager()
login_manager.init_app(app)

class Users(db.Model,UserMixin):
    __tablename__ = 'users'
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(50), nullable=False)
    password = db.Column(db.String(120), nullable=False)
    email = db.Column(db.String(50),nullable=False)
    
    def __repr__(self):
        return f'<User {self.username}>'
    
    def get_id(self):
        return self.id


@login_manager.user_loader
def load_usr(id):
    return Users.query.get(id)

bcrypt = Bcrypt(app)


@app.route('/')
def display_users():
    if current_user.is_authenticated:
        return render_template("index.html",user=True)
    else:
        return render_template("index.html",user=False)

@app.route('/login/<int:id>')
def login_usr(id):
    user = Users.query.get(id)
    login_user(user)
    return redirect('/')


@app.route('/logout')
def logout_usr():
    logout_user()
    return redirect('/')

@app.route('/create',methods=['GET',"POST"])
def create():
    if request.method == "POST":
        username = request.form["username"]
        email = request.form["email"]
        password = request.form["password"]
        
        hash_pass = bcrypt.generate_password_hash(password)

        user = Users(username=username,email=email,password=hash_pass)
        db.session.add(user)
        db.session.commit()
        return redirect(f"/login/{user.id}")
    return render_template('create.html')

@app.route('/login',methods=['get',"post"])
def login():

    if request.method == "POST":
        email = request.form["email"]
        
        user = Users.query.filter(Users.email == email).first()
        print(user)
        hash_pass = bcrypt.check_password_hash(user.password,password)
        # if hash_pass
        password = request.form["password"]

        return redirect(f"/login/{user.id}")
    return render_template('login.html')

if __name__ == "__main__":
    app.run(debug=True,host='0.0.0.0')