from flask import render_template, request, redirect, flash
from flaskr import backend
from flask_login import LoginManager, login_user, login_required, logout_user, current_user, UserMixin
import hashlib


def make_endpoints(app):
    be = backend.Backend()
    login_manager = LoginManager()
    login_manager.init_app(app)

    class User(UserMixin):
        def __init__(self, username):
            self.username = username
        @property
        def is_authenticated(self):
            return True
        def get_id(self):
            return self.username

    @login_manager.user_loader
    def load_user(user_id):
        user = User(user_id)
        return user

    # Flask uses the "app.route" decorator to call methods when users
    # go to a specific route on the project's website.
    @app.route("/")
    def home():
        if current_user.is_authenticated:
            username = current_user.username
            return render_template("main.html", user_name=username)
        else:
            return render_template("main.html")

    # TODO(Project 1): Implement additional routes according to the project requirements.

    @app.route("/signup", methods = ['GET', 'POST'])
    def signup():
        if request.method == 'POST':
            username = request.form['Username']
            password = request.form['Password']
            site_secret = "superduperteamawesome"
            with_salt = f"{username}{site_secret}{password}"
            hash = hashlib.blake2b(with_salt.encode()).hexdigest()
            password = hash
            
            if be.sign_up(username, password):
                flash("Account successfully created! Please login to continue.", category="success")
            else:
                flash("Username already exists. Please login or choose a different username.", category="error")
        return render_template('signup.html')


    @app.route("/login", methods = ['GET', 'POST'])
    def login():
        if request.method == 'POST':
            username = request.form['Username']
            password = request.form['Password']
            site_secret = "superduperteamawesome"
            with_salt = f"{username}{site_secret}{password}"
            hash = hashlib.blake2b(with_salt.encode()).hexdigest()
            password = hash

            if be.sign_in(username, password):
                user = User(username)
                login_user(user)
                flash("You have been logged in.", category="success")
            else:
                flash("Invalid username or password. Please try again.", category="error")
        return render_template('login.html')

    @app.route("/logout")
    def logout():
        logout_user()
        return render_template('logout.html')

    @login_required
    @app.route("/upload")
    def upload():
        pass