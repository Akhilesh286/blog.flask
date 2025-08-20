# app.py

from flask import Flask, render_template,redirect,request,url_for
from models import db, User

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///users.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

# Initialize database with the app
db.init_app(app)


@app.route('/')
def display_users():
    users = User.query.all()
    return render_template('display.html', users=users,update=False)


@app.route('/add_user', methods=["GET","POST"])
def add_user():
    if request.method == "POST":
        user = User(
            username=request.form["username"],
            email=request.form["email"],
        )
        db.session.add(user)
        db.session.commit()
    return redirect("/")

@app.route('/update_usr/<int:id>', methods=["GET","POST"])
def update_user(id):
    new_user = User.query.get_or_404(id)
    if request.method == "POST":
        new_user.username = request.form["username"]
        new_user.email = request.form["email"]
        db.session.commit()
    
        return redirect("/")

    users = User.query.all()
    return render_template('display.html', users=users,update=True,new_user=new_user)


@app.route('/delete_usr/<int:id>', methods=["GET","POST"])
def delete_user(id):
    user = User.query.get_or_404(id)
    db.session.delete(user)
    db.session.commit()
    return redirect('/')

if __name__ == '__main__':
    app.run(debug=True)
