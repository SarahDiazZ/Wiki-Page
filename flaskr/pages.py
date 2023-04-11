from flask import render_template, request, redirect, flash
from flaskr import backend
from flask_login import LoginManager, login_user, login_required, logout_user, current_user, UserMixin
import hashlib


def make_endpoints(app):
    """ This function defines all of the routes that this wiki has
    
    This function also initializes a 'backend.Backend()' object and a 'LoginManager()' object. 
    It associates the 'LoginManager()' object with the Flask 'app' object to manage user authentication.
    """
    be = backend.Backend()
    login_manager = LoginManager()
    login_manager.init_app(app)

    class User(UserMixin):
        """A user using the wiki.
        
        This class will create a user object for a user who has logged in.
        It will verify that the current user has been authenticated and is currently still logged in.
        This object will persist until the user logs out.

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
                True to indicate that the user is still logged in
            """
            return True

        def get_id(self):
            """Passes user id when called.
            
            Returns:
                The username of the user as their user id
            """
            return self.username

    @login_manager.user_loader
    def load_user(user_id):
        """Gets the current user based on id (username) and returns.
        
        Returns:
            Current user object
        """
        user = User(user_id)
        return user

    @app.route("/")
    def home():
        """This Flask route function renders the homepage of the website by displaying the 'main.html' template. 

        If the user is authenticated, the function retrieves the username of the currently authenticated user and passes it to the template as the 'user_name' variable. 
        If the user is not authenticated, the function doesn't display the 'main.html' template without the 'user_name' variable.
        
        Returns:
            A rendered HTML template 'main.html' which is the homepage of the website.
        """
        if current_user.is_authenticated:
            username = current_user.username
            return render_template("main.html",
                                   user_name=username,
                                   contributors=be.get_contributors())
        else:
            return render_template("main.html",
                                   contributors=be.get_contributors())

    @app.route("/signup", methods=['GET', 'POST'])
    def signup():
        """Allows the user to sign up and create an account. 

        If the response is POST, reads the username and password submitted in the form and calls the backend to create the new account if possible.
        If unsuccessful, displays error flash message prompting the user to try a different username. 
        If successful, displays success flash message prompting the user to login.

        Returns:
            The 'signup.html' template if the response is GET
        """
        if request.method == 'POST':
            username = request.form['Username']
            password = request.form['Password']
            site_secret = "superduperteamawesome"
            with_salt = f"{username}{site_secret}{password}"
            hash = hashlib.blake2b(with_salt.encode()).hexdigest()
            password = hash

            if be.sign_up(username, password):
                flash("Account successfully created! Please login to continue.",
                      category="success")
            else:
                flash(
                    "Username already exists. Please login or choose a different username.",
                    category="error")
        return render_template('signup.html')

    @app.route("/login", methods=['GET', 'POST'])
    def login():
        """Allows the user to enter their username and password to login to their account.

        If the response is POST, reads the username and password submitted in the form and calls the backend to check if it's correct.
        If unsuccessful, displays error flash message prompting the user to try again. 
        If successful, logs user in and redirects to home page.

        Returns:
            The 'login.html' template if the response is GET
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
                flash("Invalid username or password. Please try again.",
                      category="error")
        return render_template('login.html')

    @app.route("/logout")
    def logout():
        """Logs out the current authenticated user.
        
        Returns:
            The 'logout.html' template
        """
        logout_user()
        return render_template('logout.html')

    @login_required
    @app.route("/upload", methods=['GET', 'POST'])
    def upload():
        """Allows an authenticated user to upload files to the wiki.

        If the response is POST, gets the file submitted in the form.
        Checks if the file exists, and if not, displays an error flash message telling user that a file was not selected.
        If the file exists, passes it to the backend to check if it can be uploaded.
        If unsuccessful, displays error flash message. 
        If successful, displays success flask message.

        Returns:
            The 'upload.html' template if the response is GET
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
            The rendered HTML template 'pages.html' that displays a list of all available wiki pages.

        """
        return render_template("pages.html", pages=be.get_all_page_names())

    @app.route("/pages/<page_title>")
    def page_uploads(page_title):
        """This Flask route function retrives the content of a wiki page.

        It retrieves the content of a wiki page with the title that is specified in the URL using be.get_wiki_page(). It then passes the retrived content 
        to the HTML template 'pages.html' via 'render_template()'.

        Returns:
            The rendered HTML template 'pages.html' with the content of a wiki page        

        """
        content = be.get_wiki_page(page_title)
        return render_template("pages.html", page_content=content)

    @app.route("/about")
    def about():
        """Flask route function retrieves the images for us three "Camila," "Sarah," and "Ricardo". 
        The function also encodes the images in a Base64 format and passes it to the HTML template that's named 'about.html' via 'render_template()'

        Returns:
            The rendered HTML template 'about.html'. 

        """
        image_names = ["camila", "sarah", "ricardo"]
        image_data = [be.get_image(image_name) for image_name in image_names]
        return render_template('about.html',
                               image_datas=image_data,
                               base_url="https://storage.cloud.google.com/")
