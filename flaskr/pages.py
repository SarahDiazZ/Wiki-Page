from flask import render_template, request, redirect, flash
from flaskr import backend
from flask_login import LoginManager, login_user, login_required, logout_user, current_user, UserMixin
import hashlib
import base64


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

    @app.route("/")
    def home():
        if current_user.is_authenticated:
            username = current_user.username
            return render_template("main.html", user_name=username)
        else:
            return render_template("main.html")

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
                return redirect('/')
            else:
                flash("Invalid username or password. Please try again.", category="error")
        return render_template('login.html')

    @app.route("/logout")
    def logout():
        logout_user()
        return render_template('logout.html')

    @login_required
    @app.route("/upload", methods = ['GET', 'POST'])
    def upload():
        if request.method == 'POST':
            file = request.files.get("File")
            file_name = request.form['File name']
            if file:
                be.upload(file_name, file)
                flash("File uploaded successfully.", category="success")
            else:
                flash("No file selected.", category="error")
        return render_template('upload.html')

    @app.route("/pages")
    def pages():
        return render_template("pages.html", pages=be.get_all_page_names())
        
    @app.route("/pages/<page_title>")
    def page_uploads(page_title):
        content = be.get_wiki_page(page_title)
        return content

    @app.route("/about")
    def about():
        image_names = ["camila", "sarah", "ricardo"]
        image_datas = be.get_image(image_names)
        image_data = [base64.b64encode(image).decode('utf-8') for image in image_datas]
        return render_template('about.html', image_datas=image_data)

        