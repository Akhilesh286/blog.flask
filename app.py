from flask import Flask, render_template, redirect, request, url_for, abort, send_from_directory, send_file
from flask_migrate import Migrate
from flask_bcrypt import Bcrypt
from flask_login import (
    LoginManager,
    login_user,
    logout_user,
    current_user,
    login_required,
)
from sqlalchemy.orm import joinedload
from werkzeug.utils import secure_filename
from functools import wraps
from datetime import datetime
import os
import uuid
import re
from markdown import markdown

from models import db, User, Post, Profile, PostStatus

# -------------------------------------------------------------------
# App setup
# -------------------------------------------------------------------

app = Flask(__name__)

app.config["SECRET_KEY"] = "hidden-gem"
app.config["SQLALCHEMY_DATABASE_URI"] = (
    "postgresql+psycopg2://bloguser:strongpassword@localhost:5432/blogdb"
)
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False

UPLOAD_FOLDER = os.path.join(app.root_path, "media", "upload")
os.makedirs(UPLOAD_FOLDER, exist_ok=True)

db.init_app(app)
migrate = Migrate(app, db)
bcrypt = Bcrypt(app)

# -------------------------------------------------------------------
# Login manager
# -------------------------------------------------------------------

login_manager = LoginManager()
login_manager.login_view = "sign_in"
login_manager.init_app(app)


@login_manager.user_loader
def load_user(user_id):
    return db.session.get(User, int(user_id))


# -------------------------------------------------------------------
# Helpers
# -------------------------------------------------------------------

def unauthenticated_only(f):
    @wraps(f)
    def wrapper(*args, **kwargs):
        if current_user.is_authenticated:
            return redirect(url_for("index"))
        return f(*args, **kwargs)

    return wrapper


def generate_slug(title: str) -> str:
    slug = re.sub(r"[^\w\s-]", "", title.lower())
    slug = re.sub(r"[\s_-]+", "-", slug).strip("-")
    unique = slug
    counter = 1

    while Post.query.filter_by(slug=unique).first():
        unique = f"{slug}-{counter}"
        counter += 1

    return unique


@app.route('/media/<path:filename>')
def media(filename):
    return send_from_directory('media', filename)

# endpoint to get current profilepic
@app.route("/api/profile-pic")
def profile_pic():
    DEFAULT_IMAGE = os.path.join("static", "images", "prf.jpeg")

    # not logged in
    if not current_user.is_authenticated:
        return send_file(DEFAULT_IMAGE)

    profile = getattr(current_user, "profile", None)

    # no profile or no picture
    if not profile or not profile.pic:
        return send_file(DEFAULT_IMAGE)

    image_path = os.path.join("media", "uploads", profile.pic)

    # file missing on disk
    if not os.path.exists(image_path):
        return send_file(DEFAULT_IMAGE)

    return send_file(image_path)

def post_status_converter(status):
    if status == "draft":
        return PostStatus.draft
    elif status == "archived":
        return PostStatus.archived
    elif status == "published":
        return PostStatus.published
    else:
        return PostStatus.archived
    

# -------------------------------------------------------------------
# Routes
# -------------------------------------------------------------------

@app.get("/posts/load")
@login_required
def load_posts():
    page = request.args.get("page", 1, type=int)
    per_page = 10

    posts = (
        Post.query
        .filter(Post.status == PostStatus.published)
        .order_by(Post.created_at.desc())
        .paginate(page=page, per_page=per_page, error_out=False)
    )

    return render_template(
        "posts.html",
        posts=posts.items
    )


@app.route("/")
@login_required
def index():
    page = 1
    per_page = 10

    posts = (
        Post.query
        .filter(Post.status == PostStatus.published)
        .order_by(Post.created_at.desc())
        .paginate(page=page, per_page=per_page, error_out=False)
    )

    return render_template("home.html", posts=posts.items, is_user=current_user)

@app.route("/test")
def test():
    return render_template("test.html")

# -------------------------------------------------------------------

@app.route("/sign-in", methods=["GET", "POST"])
@unauthenticated_only
def sign_in():
    if request.method == "POST":
        email = request.form["email"]
        password = request.form["password"]

        user = User.query.filter_by(email=email, is_deleted=False).first()
        if not user:
            abort(401)

        if bcrypt.check_password_hash(user.password_hash, password):
            login_user(user, remember=True)
            return redirect(url_for("index"))

    return render_template("sign-in.html")


# -------------------------------------------------------------------

@app.route("/sign-up", methods=["GET", "POST"])
@unauthenticated_only
def sign_up():
    if request.method == "POST":
        username = request.form["username"]
        email = request.form["email"]
        password = request.form["password"]

        hashed = bcrypt.generate_password_hash(password).decode()

        user = User(
            username=username,
            email=email,
            password_hash=hashed,
        )

        db.session.add(user)
        db.session.commit()

        return redirect(url_for("sign_in"))

    return render_template("sign-up.html")


# -------------------------------------------------------------------

@app.route("/logout")
@login_required
def logout():
    logout_user()
    return redirect(url_for("sign_in"))


# -------------------------------------------------------------------

@app.route("/profile", methods=["GET", "POST"])
@login_required
def profile():
    profile = Profile.query.filter_by(user_id=current_user.id).first()

    if request.method == "POST":
        pic = request.files.get("pic")
        pic_name = None

        if pic and pic.filename:
            filename = secure_filename(pic.filename)
            pic_name = f"{uuid.uuid4()}_{filename}"
            pic.save(os.path.join(UPLOAD_FOLDER, pic_name))

        if not profile:
            profile = Profile(
                user_id=current_user.id,
                first_name=request.form["first_name"],
                last_name=request.form.get("last_name"),
                gender=request.form.get("gender"),
                bio=request.form.get("bio"),
                website=request.form.get("website"),
                pic=pic_name,
            )
            db.session.add(profile)
        else:
            profile.first_name = request.form["first_name"]
            profile.last_name = request.form.get("last_name")
            profile.gender = request.form.get("gender")
            profile.bio = request.form.get("bio")
            profile.website = request.form.get("website")
            if pic_name:
                profile.pic = pic_name

        db.session.commit()
        return redirect(url_for("profile"))



    return render_template(
        "profile.html",
        profile=profile,
        posts=current_user.posts,
        is_user=current_user,
    )


# -------------------------------------------------------------------

@app.route("/create", methods=["GET", "POST"])
@login_required
def create():
    if request.method == "POST":
        title = request.form["title"]

        post = Post(
            title=title,
            slug=generate_slug(title),
            description=request.form.get("description"),
            content=request.form.get("content"),
            author_id=current_user.id,
            status=post_status_converter(request.form.get("status")),
            published_at=datetime.utcnow(),
        )

        db.session.add(post)
        db.session.commit()

        return redirect(url_for("index"))

    return render_template("create.html")


# -------------------------------------------------------------------

@app.route("/post/<slug>")
def content(slug):
    post = Post.query.filter_by(
        slug=slug, status=PostStatus.published
    ).first_or_404()
    html_content = markdown(
        post.content,
        extensions=["fenced_code", "tables", "toc", "nl2br"]
    ) if post.content else None
    return render_template("content.html", post=post, is_user=current_user, content=html_content)


# -------------------------------------------------------------------

@app.post("/posts/<int:post_id>/like")
@login_required
def like_post(post_id):
    post = Post.query.get_or_404(post_id)

    # Prevent duplicate likes
    existing = PostLike.query.filter_by(
        user_id=current_user.id, post_id=post_id
    ).first()

    if existing:
        return redirect(url_for("content", post_id=post_id))

    like = PostLike(user_id=current_user.id, post_id=post_id)
    db.session.add(like)
    db.session.commit()

    return redirect(url_for("content", post_id=post_id))


# -------------------------------------------------------------------

@app.post("/posts/<int:post_id>/unlike")
@login_required
def unlike_post(post_id):
    like = PostLike.query.filter_by(
        user_id=current_user.id,
        post_id=post_id
    ).first_or_404()

    db.session.delete(like)
    db.session.commit()

    return redirect(url_for("content", post_id=post_id))


# -------------------------------------------------------------------

@app.post("/posts/<int:post_id>/comment")
@login_required
def add_comment(post_id):
    post = Post.query.get_or_404(post_id)
    content = request.form.get("content")

    if not content.strip():
        abort(400, "Comment cannot be empty")

    comment = Comment(
        content=content,
        user_id=current_user.id,
        post_id=post.id
    )

    db.session.add(comment)
    db.session.commit()

    return redirect(url_for("view_post", post_id=post.id))


# -------------------------------------------------------------------

@app.post("/comments/<int:comment_id>/reply")
@login_required
def reply_comment(comment_id):
    parent = Comment.query.get_or_404(comment_id)
    content = request.form.get("content")

    if not content.strip():
        abort(400, "Reply cannot be empty")

    reply = Comment(
        content=content,
        user_id=current_user.id,
        post_id=parent.post_id,
        parent_id=parent.id
    )

    db.session.add(reply)
    db.session.commit()

    return redirect(url_for("view_post", post_id=parent.post_id))


# -------------------------------------------------------------------

@app.post("/comments/<int:comment_id>/delete")
@login_required
def delete_comment(comment_id):
    comment = Comment.query.get_or_404(comment_id)

    if comment.user_id != current_user.id:
        abort(403)

    post_id = comment.post_id

    db.session.delete(comment)
    db.session.commit()

    return redirect(url_for("view_post", post_id=post_id))


# -------------------------------------------------------------------

@app.post("/posts/<int:post_id>/bookmark")
@login_required
def bookmark_post(post_id):
    post = Post.query.get_or_404(post_id)

    existing = Bookmark.query.filter_by(
        user_id=current_user.id,
        post_id=post_id
    ).first()

    if existing:
        return redirect(url_for("view_post", post_id=post_id))

    bookmark = Bookmark(
        user_id=current_user.id,
        post_id=post_id
    )

    db.session.add(bookmark)
    db.session.commit()

    return redirect(url_for("view_post", post_id=post_id))


# -------------------------------------------------------------------

@app.post("/posts/<int:post_id>/unbookmark")
@login_required
def unbookmark_post(post_id):
    bookmark = Bookmark.query.filter_by(
        user_id=current_user.id,
        post_id=post_id
    ).first_or_404()

    db.session.delete(bookmark)
    db.session.commit()

    return redirect(url_for("view_post", post_id=post_id))


# -------------------------------------------------------------------

@app.post("/users/<int:user_id>/follow")
@login_required
def follow_user(user_id):
    user = User.query.get_or_404(user_id)

    if user.id == current_user.id:
        abort(400, "You cannot follow yourself")

    existing = Follow.query.filter_by(
        follower_id=current_user.id,
        following_id=user_id
    ).first()

    if existing:
        return redirect(url_for("profile", user_id=user_id))

    follow = Follow(
        follower_id=current_user.id,
        following_id=user_id
    )
    db.session.add(follow)
    db.session.commit()

    return redirect(url_for("profile", user_id=user_id))


# -------------------------------------------------------------------

@app.post("/users/<int:user_id>/unfollow")
@login_required
def unfollow_user(user_id):
    follow = Follow.query.filter_by(
        follower_id=current_user.id,
        following_id=user_id
    ).first_or_404()

    db.session.delete(follow)
    db.session.commit()

    return redirect(url_for("profile", user_id=user_id))


# -------------------------------------------------------------------

@app.route("/search")
def search():
    query = request.args.get("title")
    posts = []

    if query:
        posts = Post.query.filter(
            Post.title.ilike(f"%{query}%"),
            Post.status == PostStatus.published,
        ).all()

    return render_template("search.html", posts=posts, is_user=current_user)


# -------------------------------------------------------------------

@app.route("/delete/<int:post_id>")
@login_required
def delete(post_id):
    post = Post.query.get_or_404(post_id)

    if post.author_id != current_user.id:
        abort(403)

    post.status = PostStatus.archived
    db.session.commit()

    return redirect(url_for("profile"))


# -------------------------------------------------------------------

if __name__ == "__main__":
    app.run(debug=True)
