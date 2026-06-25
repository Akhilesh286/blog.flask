from flask import (
    Flask,
    render_template, 
    redirect, 
    request,
    url_for, 
    abort, 
    send_from_directory, 
    send_file,
    make_response,
    Blueprint
)
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
import os
import uuid
import re
from markdown import markdown
import humanize
from datetime import datetime, timezone

from models import db, User, Post, Profile, PostStatus, PostLike, Comment, Bookmark, Follow

from routes.comments import comments_bp

# -------------------------------------------------------------------
# App setup
# -------------------------------------------------------------------

app = Flask(__name__)

app.config["SECRET_KEY"] = "hidden-gem"
app.config["SQLALCHEMY_DATABASE_URI"] = (
    "postgresql+psycopg2://chatapp:J8nH?32s@localhost:5432/blogdb"
)
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False

UPLOAD_FOLDER = os.path.join(app.root_path, "media", "uploads")
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
# Blueprint
# -------------------------------------------------------------------

app.register_blueprint(comments_bp)

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

    profile = getattr(current_user, "profile", None)

    # no profile or no picture
    if not profile or not profile.pic:
        return send_file(DEFAULT_IMAGE)

    image_path = os.path.join("media", "uploads", profile.pic)

    # file missing on disk
    if not os.path.exists(image_path):
        return send_file(DEFAULT_IMAGE)

    return send_file(image_path)

# endpoint to get current profilepic
@app.route("/components/profile-pic")
def profile_pic_img():
    return render_template('/components/profile-pic.html')


def post_status_converter(status):
    if status == "draft":
        return PostStatus.draft
    elif status == "archived":
        return PostStatus.archived
    elif status == "published":
        return PostStatus.published
    else:
        return PostStatus.archived


@app.template_filter("timeago")
def timeago_filter(dt):
    if not dt:
        return ""
    now = datetime.now(timezone.utc)
    return humanize.naturaltime(now - dt)


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

    return render_template("home.html", posts=posts.items)

@app.route("/test")
def test():
    users = User.query.all()
    return render_template("test.html", users=users)

# -------------------------------------------------------------------

@app.route("/@<username>")
def profile(username):
    if not re.match(r'^[A-Za-z0-9_]+$', username):
        return abort(404)

    user = User.query.filter_by(username=username).first()
    if not user:
        return abort(404)

    return render_template("profile.html", profile=user.profile,user=user, is_current_user=False)


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
def user_profile():
    profile = Profile.query.filter_by(user_id=current_user.id).first()
    posts = current_user.posts.filter(Post.status == PostStatus.published).all()

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
        posts=posts,
        user=current_user,
        is_current_user=True
    )

# -------------------------------------------------------------------

@app.route("/dashboard")
@login_required
def dashboard():
    return render_template('dashboard.html')

# -------------------------------------------------------------------

@app.route("/create", methods=["GET", "POST"])
@login_required
def create_post():
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

    return render_template("editor.html")


# -------------------------------------------------------------------

@app.route("/post/<slug>")
def content(slug):
    post = Post.query.filter_by(slug=slug).first_or_404()
    is_author = (post.author_id == current_user.id)

    if not is_author and post.status != PostStatus.published:
        abort(404)

    html_content = markdown(
        post.content,
        extensions=["fenced_code", "tables", "toc", "nl2br"]
    ) if post.content else None
    return render_template("content.html", post=post, content=html_content)


# -------------------------------------------------------------------

@app.post("/posts/<int:post_id>/like")
@login_required
def toggle_like(post_id):
    post = Post.query.get_or_404(post_id)

    existing = PostLike.query.filter_by(
        user_id=current_user.id, post_id=post_id
    ).first()

    if existing:
        # UNLIKE
        db.session.delete(existing)
        db.session.commit()
    else:
        # LIKE
        like = PostLike(user_id=current_user.id, post_id=post_id)
        db.session.add(like)
        db.session.commit()

    # Return updated like section (HTMX partial)
    return render_template("like-section.html", post=post)


# -------------------------------------------------------------------

@app.post("/posts/<int:post_id>/bookmark")
@login_required
def toggle_bookmark(post_id):
    post = Post.query.get_or_404(post_id)

    existing = Bookmark.query.filter_by(
        user_id=current_user.id,
        post_id=post_id
    ).first()

    if existing:
        # UNBOOKMARK
        db.session.delete(existing)
        db.session.commit()
    else:
        # BOOKMARK
        bookmark = Bookmark(
            user_id=current_user.id,
            post_id=post_id
        )
        db.session.add(bookmark)
        db.session.commit()

    db.session.refresh(post)

    return render_template("bookmark-section.html", post=post)


# -------------------------------------------------------------------

@app.post("/users/<int:user_id>/follow")
@login_required
def toggle_follow(user_id):

    if user_id == current_user.id:
        return "Cannot follow yourself", 400

    target_user = User.query.get_or_404(user_id)

    existing = Follow.query.filter_by(
        follower_id=current_user.id,
        following_id=user_id
    ).first()

    if existing:
        db.session.delete(existing)
    else:
        new_follow = Follow(
            follower_id=current_user.id,
            following_id=user_id
        )
        db.session.add(new_follow)

    db.session.commit()

    # Required for component rendering
    is_following = Follow.query.filter_by(
        follower_id=current_user.id,
        following_id=user_id
    ).first()

    element_id = f"c-follow-{user_id}"

    return render_template(
        "follow-section.html",
        user_id=user_id,
        is_following=is_following
    )


# -------------------------------------------------------------------

@app.route("/search")
def search():
    return render_template("search.html", is_user=current_user)


# -------------------------------------------------------------------

@app.route("/search-posts")
def search_posts():
    query = request.args.get("q", "").strip()

    # No query → show search page
    if not query:
        return ""

    # Query exists → fetch results
    results = (
        Post.query.filter(Post.title.ilike(f"%{query}%"))
        .order_by(Post.created_at.desc())
        .limit(10)
        .all()
    )

    return render_template(
        "search-posts.html",
        posts=results
    )


# -------------------------------------------------------------------

@app.route("/search-people")
def search_people():
    query = request.args.get("q", "").strip()

    # No query → show search page
    if not query:
        return ""

    # Query exists → fetch results
    results = User.query.filter(User.username.ilike(f"%{query}%")).limit(10).all()


    return render_template(
        "users.html",
        users=results
    )


# -------------------------------------------------------------------

@app.route("/posts/<int:post_id>/publish")
@login_required
def publish_post(post_id):
    post = Post.query.get_or_404(post_id)

    if post.author_id != current_user.id:
        abort(403)

    post.status = PostStatus.published
    db.session.commit()

    return redirect(request.referrer or url_for("index"))

# -------------------------------------------------------------------

@app.route("/posts/<int:post_id>/update", methods=["GET", "POST"])
@login_required
def update_post(post_id):
    post = Post.query.get_or_404(post_id)

    if request.method == "POST":
        title = request.form["title"]
        slug = generate_slug(title)
        status = post_status_converter(request.form.get("status"))
        
        post.title=title
        post.slug=slug
        post.description=request.form.get("description")
        post.content=request.form.get("content")
        post.status=status

        db.session.add(post)
        db.session.commit()
        if status == PostStatus.draft:
            return redirect(url_for('index'))
        return redirect(url_for("content",slug=slug))

    # GET -> show update page
    return render_template("editor.html", post=post)

# -------------------------------------------------------------------

@app.route("/posts/<int:post_id>/archive")
@login_required
def archive_post(post_id):
    post = Post.query.get_or_404(post_id)

    if post.author_id != current_user.id:
        abort(403)

    post.status = PostStatus.archived
    db.session.commit()

    return redirect(request.referrer or url_for("index"))



# -------------------------------------------------------------------

@app.get("/posts/confirm-delete/<int:post_id>")
def confirm_delete(post_id):
    post = Post.query.get_or_404(post_id)
    return render_template("modals/delete-post.html", post=post)

# -------------------------------------------------------------------

@app.delete("/posts/<int:post_id>")
@login_required
def delete_post(post_id):
    post = Post.query.get_or_404(post_id)

    if post.author_id != current_user.id:
        abort(403)

    db.session.delete(post)
    db.session.commit()

    # HTMX loves 204 (no content)
    response = make_response("", 204)
    response.headers["HX-Refresh"] = "true"
    return response
# -------------------------------------------------------------------

@app.get("/dashboard/drafts")
def dashboard_drafts():
    page = request.args.get("page", 1, type=int)
    per_page = 10

    stmt = (
        db.select(Post)
        .where(
            Post.author_id == current_user.id,
            Post.status == PostStatus.draft
        )
        .order_by(Post.id.desc())
    )

    posts = db.paginate(stmt, page=page, per_page=per_page, error_out=False)

    return render_template("dashboard/drafts.html", posts=posts)


# -------------------------------------------------------------------
@app.get("/dashboard/likes")
@login_required
def dashboard_likes():
    page = request.args.get("page", 1, type=int)
    per_page = 10

    posts = (
        Post.query
            .join(PostLike)
            .filter(PostLike.user_id == current_user.id)
            .order_by(Post.id.desc())
            .paginate(page=page, per_page=per_page, error_out=False)
    )

    return render_template("dashboard/likes.html", posts=posts)



# -------------------------------------------------------------------

@app.get("/dashboard/archive")
def dashboard_archive():
    page = request.args.get("page", 1, type=int)
    per_page = 10

    stmt = (
        db.select(Post)
        .where(
            Post.author_id == current_user.id,
            Post.status == PostStatus.archived
        )
        .order_by(Post.id.desc())
    )

    posts = db.paginate(stmt, page=page, per_page=per_page, error_out=False)

    return render_template("dashboard/archive.html", posts=posts)


# -------------------------------------------------------------------

@app.get("/dashboard/comments")
def dashboard_comments():
    return render_template("dashboard/comments.html")


# -------------------------------------------------------------------

@app.get("/dashboard/connections")
def dashboard_connections():
    page = request.args.get("page", 1, type=int)

    followers_users = (
        User.query
            .join(Follow, Follow.follower_id == User.id)
            .filter(Follow.following_id == current_user.id)
            .paginate(page=page, per_page=20, error_out=False)
    )

    following_users = (
        User.query
            .join(Follow, Follow.following_id == User.id)
            .filter(Follow.follower_id == current_user.id)
            .paginate(page=page, per_page=20, error_out=False)
    )
    
    return render_template("dashboard/connections.html", followers_users=followers_users, following_users=following_users)



# -------------------------------------------------------------------

@app.get("/dashboard/followers")
def dashboard_followers():
    page = request.args.get("page", 1, type=int)

    return render_template("dashboard/followers.html")


# -------------------------------------------------------------------

@app.get("/dashboard/security")
def dashboard_security():
    return render_template("dashboard/security.html")



# -------------------------------------------------------------------

@app.get("/dashboard/phone")
def dashboard_phone():
    return render_template("dashboard/phone_verification.html")



# -------------------------------------------------------------------

@app.get("/dashboard/email")
def dashboard_email():
    return render_template("dashboard/email_verification.html")



# -------------------------------------------------------------------

@app.get("/dashboard/2fa")
def dashboard_2fa():
    return render_template("dashboard/two_factor.html")



# -------------------------------------------------------------------

@app.get("/dashboard/logout")
def dashboard_logout():
    return render_template("dashboard/logout.html")
    # OR redirect to logout logic if you want



# -------------------------------------------------------------------

@app.get("/dashboard/about")
def dashboard_about():
    return render_template("dashboard/about.html")



# -------------------------------------------------------------------

@app.get("/dashboard/help")
def dashboard_help():
    return render_template("dashboard/help.html")



# -------------------------------------------------------------------

@app.get("/dashboard/bookmarks")
def dashboard_bookmarks():
    posts = (
        Post.query
            .join(Bookmark)
            .filter(Bookmark.user_id == current_user.id)
            .order_by(Post.id.desc())
            .all()
    )
    return render_template("dashboard/bookmarks.html", posts=posts)


if __name__ == "__main__":
    app.run(debug=True)
