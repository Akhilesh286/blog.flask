from flask import Flask, render_template,redirect,request,url_for
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from flask_bcrypt import Bcrypt
from flask_login import LoginManager,UserMixin,login_user,logout_user,current_user,login_required
from models import db, User, Post, Profile
from werkzeug.utils import secure_filename

from functools import wraps

import uuid 
import os



app = Flask(__name__)


# Sql configuration
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///blog.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db.init_app(app)
migrate = Migrate(app,db)
# os.makedirs(os.path.join(app.config["UPLOAD_IMAGE"]), exist_ok=True)
# User management
app.secret_key = 'hidden gem'
login_manager = LoginManager()
login_manager.login_view = 'sign_in'
login_manager.init_app(app)
bcrypt = Bcrypt(app)

UPLOAD_FOLDER = os.path.join(app.root_path, 'static', 'upload')
# os.makedirs(UPLOAD_FOLDER, exist_ok=True)


@login_manager.user_loader
def load_usr(id):
    return User.query.get(id)



def unauthenticated_only(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if current_user.is_authenticated:
            return redirect(url_for('index'))  # or any other page
        return f(*args, **kwargs)
    return decorated_function


@app.route('/', methods=['GET'])
@login_required
def index():
    is_user = current_user
    get_by = request.args.get('getBy')
    is_latest = True
    posts = None
    if get_by == 'latest':
        posts = Post.query.order_by(Post.created_at.desc()).limit(50).all()
        is_latest = True
    elif get_by == 'oldest':
        posts = Post.query.order_by(Post.created_at.asc()).limit(50).all()
        is_latest = False
    else:
        posts = Post.query.order_by(Post.created_at.desc()).limit(50).all()
    return render_template('home.html',is_user=is_user,posts=posts,isLatest=is_latest)
        
@app.route('/sign-in',methods=["GET","POST"])
@unauthenticated_only
def sign_in():
    if request.method == "POST":
        email = request.form["email"]
        password = request.form["password"]

        user = User.query.filter(User.email==email).first()
        auth = bcrypt.check_password_hash(user.password,password)
        if auth:
            login_user(user)
            return redirect("/")
        
    return render_template('sign-in.html')

@app.route('/sign-up',methods=["GET","POST"])
def sign_up():
    if request.method == "POST":
        username = request.form["username"]
        email = request.form["email"]
        password = request.form["password"]

        hash_pass = bcrypt.generate_password_hash(password)

        user = User(username=username,email=email,password=hash_pass)
        db.session.add(user)
        db.session.commit()

        return redirect('/sign-in')

    return render_template('sign-up.html')



@app.route('/logout',methods=["GET","POST"])
@login_required
def logout():
    logout_user()
    return redirect("/")

@app.route('/profile',methods=["GET","POST"])
@login_required
def profile():
    profile = Profile.query.filter_by(user_id=current_user.id).first()
    print(f"profile: {profile}")
    if request.method == "POST":
        firstname = request.form["firstname"]
        lastname = request.form["lastname"]
        phone = request.form["phone"]
        gender = request.form["gender"]
        bio = request.form["bio"]
        website = request.form["website"]
        pic = request.files["pic"]
        pic_filename = secure_filename(pic.filename)
        # set uuid
        pic_name = str(uuid.uuid1()) + '_' + pic_filename

        # save the image

        if profile is None:
            profile = Profile(user_id=current_user.id, firstname=firstname, lastname=lastname, phone=phone, gender=gender, bio=bio, website=website, pic=pic_name)
            db.session.add(profile)
        else:
            profile.firstname = firstname
            profile.lastname = lastname
            profile.phone = phone
            profile.gender = gender
            profile.bio = bio
            profile.website = website
            profile.pic = pic_name
        try:
            db.session.commit()
            pic.save(os.path.join(UPLOAD_FOLDER, pic_name))
        except:
            print("error \n\n\n")
    is_user = current_user
    posts = current_user.posts
    return render_template('profile.html',is_user=is_user,posts=posts, profile=profile)

@app.route('/create',methods=["GET","POST"])
@login_required
def create():
    is_user = current_user.is_authenticated
    if request.method == "POST":
        title = request.form["title"]
        description = request.form["description"]
        content = request.form["content"]

        post = Post(title=title,description=description,content=content,user_id=current_user.id)
        db.session.add(post)
        db.session.commit()
    
        return redirect('/')
    return render_template('create.html',is_user=is_user)

@app.route('/content/<int:id>')
def content(id):
    post = Post.query.get(id)
    return render_template('content.html',post=post)

@app.route('/search', methods=['GET'])
def search():
    is_user = current_user
    search_term = request.args.get('title')
    if search_term:
        results = Post.query.filter(Post.title.ilike(f"%{search_term}%")).all()
        return render_template('search.html', posts=results, is_user=is_user)

    return render_template('search.html', is_user=is_user)

@app.route('/update/<int:id>', methods=['GET', 'POST'])
def update(id):
    post = Post.query.get(id)
    if request.method == "POST":
        post.title = request.form["title"]
        post.description = request.form["description"]
        post.content = request.form["content"]

        db.session.commit()    
        return redirect('/dashboard')
    return render_template('update.html',post=post)

@app.route('/delete/<int:id>')
def delete(id):
    post = Post.query.get(id)
    db.session.delete(post)
    db.session.commit()
    return redirect('/dashboard')


if __name__ == '__main__':
    app.run(debug=True)
