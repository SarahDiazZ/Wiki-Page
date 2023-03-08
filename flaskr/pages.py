from flask import render_template, request, redirect, flash
from flaskr import backend
from flask_login import LoginManager, login_user, login_required, logout_user, current_user, UserMixin
import hashlib
import base64


def make_endpoints(app):
    """
    """
    be = backend.Backend()
    login_manager = LoginManager()
    login_manager.init_app(app)

    class User(UserMixin):
        """A user using the wiki.
        
        Detailed explanation of class and what it implements

        Attributes:
            username: A String containing the username of the user.
        """
        def __init__(self, username):
            """Initializes user with given username."""
            self.username = username

        @property
        def is_authenticated(self):
            """Indicates if the user is logged in or not.
            
            Returns:

            """
            return True

        def get_id(self):
            """Returns the username of the user as their user id.
            
            Returns:

            """
            return self.username

    @login_manager.user_loader
    def load_user(user_id):
        """Gets the current user based on id (username) and returns.
        
        Returns:

        """
        user = User(user_id)
        return user

    @app.route("/")
    def home():
        """This Flask route function renders the homepage of the website by displaying the 'main.html' template. 

        If the user is authenticated, the function retrieves the username of the currently authenticated user and passes it to the template as the 'user_name' variable. 
        If the user is not authenticated, the function doesn't display the 'main.html' template without the 'user_name' variable.
        
        Returns:

        """
        if current_user.is_authenticated:
            username = current_user.username
            return render_template("main.html", user_name=username)
        else:
            return render_template("main.html")

    @app.route("/signup", methods = ['GET', 'POST'])
    def signup():
        """This Flask route function renders the 'signup.html' template if the response is GET. 
        If the response is POST, the function reads the username and password submitted in the form and calls the backend to create the new account, if possible.
        If unsuccessful, an error flash message is displayed prompting the user to try a different username. 
        If successful, a success flash message is displayed prompting the user to login with the username and password they just made.

        Returns:

        """
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
        """This Flask route function renders the 'login.html' template if the response is GET.
        If the response is POST, the function reads the username and password submitted in the form and calls the backend to check if it's correct.
        If unsuccessful, an error flash message is displayed prompting the user to try again. 
        If successful, the user is logged in and redirected to the home page.

        Returns:

        """
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
        """This Flask route function renders the 'logout.html' template and logs out the current authenticated user.
        
        Returns:
            
        """
        logout_user()
        return render_template('logout.html')

    @login_required
    @app.route("/upload", methods = ['GET', 'POST'])
    def upload():
        """This Flask route function renders the 'upload.html' template if the response is GET.
        If the response is POST, the function gets the file submitted in the form and passes it to the backend to check if it can be uploaded.
        If unsuccessful, an error flash message is displayed and the file is not uploaded. 
        If successful, a success flask message is displayed and the file is uploaded.

        Returns:

        """
        if request.method == 'POST':
            file = request.files.get("File")
            file_name = request.form['File name']
            if file:
                if be.upload(file_name, file):
                    flash("File uploaded successfully.", category="success")
                else:
                    flash("File name is taken.", category="error")
            else:
                flash("No file selected.", category="error")
        return render_template('upload.html')

    @app.route("/pages")
    def pages():
        """This Flask route function renders a page that displays a list of all available wiki pages.
        It displays the wiki pages by calling the 'be.get_all_page_name()' function. Then it passes the list of pages names
        to the HTML template 'pages.html' with 'render_template()'.

        Returns:

        """
        return render_template("pages.html", pages=be.get_all_page_names())
 
    @app.route("/pages/<page_title>")
    def page_uploads(page_title):
        """This Flask route function retrives the content of a wiki page.

        It retrieves the content of a wiki page with the title that is specified in the URL using be.get_wiki_page(). It then passes the retrived content 
        to the HTML template 'pages.html' via 'render_template()'.

        Returns:

        """   
        content = be.get_wiki_page(page_title)
        return render_template("pages.html", page_content=content)

    @app.route("/about")
    def about():
        """Flask route function retrieves the images for us three "Camila," "Sarah," and "Ricardo". 
        The function also encodes the images in a Base64 format and passes it to the HTML template that's named 'about.html' via 'render_template()'

        Returns:

        """
        image_names = ["camila", "sarah", "ricardo"]
        image_datas = be.get_image(image_names)
        image_data = [base64.b64encode(image).decode('utf-8') for image in image_datas]
        return render_template('about.html', image_datas=image_data)

        