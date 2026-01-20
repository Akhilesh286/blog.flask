from flask import Flask,render_template ,request,redirect,url_for
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy.orm import DeclarativeBase

class Base(DeclarativeBase):
  pass

# create the app
app = Flask(__name__)

db = SQLAlchemy(model_class=Base)
app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///project.db"
db.init_app(app)

# with app.app_context():
#     db.create_all()

from sqlalchemy import Integer, String
from sqlalchemy.orm import Mapped, mapped_column

class User(db.Model):
    id: Mapped[int] = mapped_column(primary_key=True)
    username: Mapped[str] = mapped_column(unique=True)
    email: Mapped[str]


@app.route("/create", methods=["GET", "POST"])
def user_create():
    if request.method == "POST":
        user = User(
            username=request.form["username"],
            email=request.form["email"],
        )
        db.session.add(user)
        db.session.commit()
        return redirect(url_for("display_users"))

    return render_template("create.html")

@app.route("/delete", methods=["GET", "POST"])
def user_delete():

    if request.method == "POST":
        id = request.form["item"]
        user = db.get_or_404(User, id)
        db.session.delete(user)
        db.session.commit()
        return redirect(url_for("display_users"))

    return render_template("delete.html", user=user)

@app.route('/')
def display_users():
    users = db.session.execute(db.select(User).order_by(User.username)).scalars()
    return render_template('index.html', users=users)

if __name__ == '__main__':
    app.run(debug=True)