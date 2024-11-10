from flask import Flask, render_template

app = Flask(__name__)

@app.route('/')
def index():
    return render_template('home.html')

@app.route('/sign-in')
def sign_in():
    return render_template('sign-in.html')

@app.route('/sign-up')
def sign_up():
    return render_template('sign-up.html')

@app.route('/profile')
def profile():
    return render_template('profile.html')

@app.route('/create')
def create():
    return render_template('create.html')

@app.route('/save')
def save():
    return render_template('save.html')

if __name__ == '__main__':
    app.run(debug=True)
