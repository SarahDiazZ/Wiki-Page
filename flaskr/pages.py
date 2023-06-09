from flask import render_template, request, redirect, flash, jsonify
from flaskr import backend
from flask_login import LoginManager, login_user, login_required, logout_user, current_user, UserMixin
import hashlib
import string


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

        def get_profile_picture(self):
            """Retrieves user's profile picture.
            
            Returns:
                Base url added to location of profile picture from Backend.
            """
            return "https://storage.cloud.google.com/awesomewikicontent/" + be.get_profile_pic(
                self.username)

    @login_manager.user_loader
    def load_user(user_id):
        """Gets the current user based on id (username) and returns.
        
        Returns:
            Current user object
        """
        user = User(user_id)
        return user

    def validate_password(password):
        """Validates that the password passed to it fulfills all requirements.
        
        Ensures that the password is 8 or more characters long and contains at least 1 letter, 1 special character, and 1 number.
        
        Returns:
            True if the password fulfills the requirements.
            False if the password does not fulfill all requirements.
        """
        if len(password) >= 8:
            specials = string.punctuation
            nums = string.digits
            letters = string.ascii_letters
            has_special = False
            has_num = False
            has_letter = False

            for char in password:
                if char in specials:
                    has_special = True
                elif char in nums:
                    has_num = True
                elif char in letters:
                    has_letter = True
            return has_special and has_num and has_letter
        return False

    def hash_password(username, password):
        """Hashes the password passed to it.
        
        Returns:
            Hashed password
        """
        site_secret = "superduperteamawesome"
        with_salt = f"{username}{site_secret}{password}"
        hashed = hashlib.blake2b(with_salt.encode()).hexdigest()
        return hashed

    @app.route("/", methods=['GET', 'POST'])
    def home():
        """This Flask route function renders the homepage of the website by displaying the 'main.html' template.
        
        Returns:
            A rendered HTML template 'main.html' which is the homepage of the website.
        """
        return render_template("main.html",
                               pages=be.get_all_page_names(),
                               contributors=be.get_contributors())

    @app.route("/signup", methods=['GET', 'POST'])
    def signup():
        """Allows the user to sign up and create an account. 

        If the response is POST, reads the username and password submitted in the form and calls the backend to create the new account if possible.
        If unsuccessful, displays error flash message prompting the user to try a different username. 
        If successful, logs the user in and redirects to the home page.

        Returns:
            The 'signup.html' template if the response is GET.
            The 'main.html' template if the account is successfully created.
        """
        if request.method == 'POST':
            username = request.form['Username']
            password = request.form['Password']
            if validate_password(password):
                password = hash_password(username, password)

                if be.sign_up(username, password):
                    user = User(username)
                    login_user(user)
                    return render_template("main.html",
                                           pages=be.get_all_page_names(),
                                           contributors=be.get_contributors())
                else:
                    flash(
                        "Username already exists. Please login or choose a different username.",
                        category="error")
            else:
                flash(
                    "Your new password does not meet the requirements. Please make sure that it is 8 or more characters long and has at least 1 letter, 1 number, and 1 special symbol.",
                    category="error")
        return render_template('signup.html', pages=be.get_all_page_names())

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
        return render_template('login.html', pages=be.get_all_page_names())

    @app.route("/logout")
    def logout():
        """Logs out the current authenticated user.
        
        Returns:
            The 'logout.html' template
        """
        logout_user()
        return render_template('logout.html', pages=be.get_all_page_names())

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
                if be.upload(current_user.username, file_name, file):
                    flash("File uploaded successfully.", category="success")
                else:
                    flash("File name is taken.", category="error")
            else:
                flash("No file selected.", category="error")
        return render_template('upload.html', pages=be.get_all_page_names())

    @app.route("/pages")
    def pages():
        """This Flask route function renders a page that displays a list of all available wiki pages.
        It displays the wiki pages by calling the 'be.get_all_page_name()' function. Then it passes the list of pages names
        to the HTML template 'pages.html' with 'render_template()'.

        Returns:
            The rendered HTML template 'pages.html' that displays a list of all available wiki pages.

        """
        return render_template("pages.html", wiki_pages=be.get_all_page_names())

    @app.route("/pages/<page_title>")
    def page_uploads(page_title):
        """This Flask route function retrives the content of a wiki page.

        It retrieves the content of a wiki page with the title that is specified in the URL using be.get_wiki_page(). It then passes the retrived content 
        to the HTML template 'pages.html' via 'render_template()'.

        Returns:
            The rendered HTML template 'pages.html' with the content of a wiki page        

        """

        content = be.get_wiki_page(page_title)
        return render_template("pages.html",
                               page_content=content,
                               pages=be.get_all_page_names())

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
                               base_url="https://storage.cloud.google.com/",
                               pages=be.get_all_page_names())

    @login_required
    @app.route("/profile", methods=['GET', 'POST'])
    def profile():
        """Displays the profile page where user can change username and password, update profile picture, and delete their uploaded files.

        Returns:
            The rendered HTML template 'profile.html'.

        """
        files = be.get_user_files(current_user.username)
        num_files = len(files)

        return render_template(
            'profile.html',
            file_num=num_files,
            files=files,
            pages=be.get_all_page_names(),
            default=
            "https://storage.cloud.google.com/awesomewikicontent/default-profile-pic.gif"
        )

    @login_required
    @app.route("/upload-pfp", methods=['GET', 'POST'])
    def upload_profile_picture():
        """Allows user to upload a new profile picture.

        If no file is submitted or backend is unable to change profile picture, displays error flash message.
        If backend successfully changes profile picture, displays success flash message.

        Returns:
            The rendered HTML template 'profile.html'.

        """
        if request.method == 'POST':
            pfp = request.files.get("File")
            if pfp:
                if be.change_profile_picture(current_user.username, pfp, False):
                    flash("Successfully updated profile picture.",
                          category="success")
                else:
                    flash(
                        "Could not update profile picture. Accepted file types: png, jpg, jpeg, gif",
                        category="error")
            else:
                flash("No file selected.", category="error")

        return profile()

    @login_required
    @app.route("/remove-pfp", methods=['GET', 'POST'])
    def remove_profile_picture():
        """Allows user to remove their current profile picture and restore default picture.

        Calls Backend and displays flash success message.

        Returns:
            The rendered HTML template 'profile.html'.

        """
        if request.method == 'POST':
            be.change_profile_picture(current_user.username, None, True)
            flash("Successfully removed profile picture.", category="success")

        return profile()

    @login_required
    @app.route("/delete", methods=['GET', 'POST'])
    def delete_file():
        """Allows user to delete a file they uploaded.

        Calls Backend and displays flash success message.

        Returns:
            The rendered HTML template 'profile.html'.

        """
        if request.method == 'POST':
            file_name = request.form.get('file_name')
            be.delete_uploaded_file(current_user.username, file_name)
            flash("Successfully removed file: '" + file_name + "'",
                  category="success")
        return profile()

    @login_required
    @app.route("/change_password", methods=['GET', 'POST'])
    def change_password():
        """Allows user to change their password.

        If user leaves one or both fields blank, displays error flash message.
        If user enters the same password for current and new password, displays error flash message.
        If password does not fulfill requirements, displays error flash message.
        If current password is incorrect, displays error flash message.
        If Backend successfully changes password, displays success flash message.

        Returns:
            The rendered HTML template 'profile.html'.

        """
        if request.method == 'POST':
            curr_pass = request.form['CurrentPassword']
            new_pass = request.form['NewPassword']

            if not curr_pass or not new_pass:
                flash("Please fill in both required fields.", category="error")

            elif curr_pass == new_pass:
                flash("Passwords cannot match. Please try again.",
                      category="error")

            elif validate_password(new_pass):
                new_pass = hash_password(current_user.username, new_pass)
                curr_pass = hash_password(current_user.username, curr_pass)

                if be.change_password(current_user.username, curr_pass,
                                      new_pass):
                    flash("Successfully updated password!", category="success")
                else:
                    flash("Incorrect current password. Please try again.",
                          category="error")
            else:
                flash(
                    "Your new password does not meet the requirements. Please make sure that it is 8 or more characters long and has at least 1 letter, 1 number, and 1 special symbol.",
                    category="error")

        return profile()

    @login_required
    @app.route("/change_username", methods=['GET', 'POST'])
    def change_username():
        """Allows user to change their username.

        If user leaves field blank, displays error flash message.
        If user enters the same username as their current username, displays error flash message.
        If username is taken, displays error flash message.
        If Backend successfully changes username, displays success flash message.

        Returns:
            The rendered HTML template 'profile.html'.

        """
        new_username = request.form['Username']
        if request.method == 'POST':
            if not new_username:
                flash("Please fill in the required field.", category="error")
            elif new_username == current_user.username:
                flash("New username cannot match current username.",
                      category="error")
            elif be.change_username(current_user.username, new_username):
                user = User(new_username)
                login_user(user)
                flash("Successfully updated username!", category="success")
            else:
                flash("Username is already taken. Please try again.",
                      category="error")
        return profile()

    @app.route("/FAQ", methods=['GET', 'POST'])
    def faq_page():
        '''Displays the Frequently Asked Question (FAQ) page

        This displays the FAQ page with a list of all questions and their answers.

        Returns:
            The result of calling the render_template() function, which renders the FAQ page template with the list of questions and all available page names.
        '''
        questions = be.get_faq()
        return render_template("faq.html",
                               questions=questions,
                               pages=be.get_all_page_names())

    @app.route("/submit_question", methods=['GET', 'POST'])
    def submit_question():
        '''Handles the submission of a new FAQ question

        This handles the submission of a question via a GET or POST request, updates the list of questions with the user's new question, and redirects the user to the FAQ page.

        Returns:
            The result of calling the faq_page() function, which renders the FAQ page with updated information.
        '''
        if request.method == 'POST':
            question = request.form['question']
            if not question:
                flash("Please enter a question.", category="error")
            else:
                be.submit_question(current_user.username, question)
                flash("Successfully submitted question.", category="success")
        return faq_page()

    @app.route("/submit_reply", methods=['GET', 'POST'])
    def submit_reply():
        '''Handles the submission of a reply to a FAQ question

        This handles the submission of a reply to a FAQ question via a GET or POST request, updates the FAQ question with the user's reply, and redirects the user to the FAQ page.

        Returns:
            The result of calling the faq_page() function, which renders the FAQ page with updated information.        
        '''
        if request.method == 'POST':
            reply = request.form['reply']
            question = request.form['index']
            if not reply:
                flash("Please enter a reply.", category="error")
            else:
                be.submit_reply(current_user.username, reply, question)
                flash("Successfully submitted reply.", category="success")
        return faq_page()

    @app.route('/search-results', methods=['POST'])
    def search_results():
        """Displays all matching search results on search page.

        Obtains list of matching results from search and displays the page links. If there are no matching results, passes empty list to HTML file.

        Returns:
            The rendered HTML template 'search.html'.     
        """

        search_input = request.form['SearchInput']
        matching_results = request.form['MatchingResults']
        suggested_pages = matching_results.split(',')
        if suggested_pages[0] == "":
            suggested_pages = []

        return render_template('search.html',
                               suggestions=suggested_pages,
                               search_value=search_input,
                               pages=be.get_all_page_names())
