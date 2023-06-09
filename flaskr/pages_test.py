from flaskr import create_app, backend
from flask import url_for, Flask
from flask_login import LoginManager, login_user, login_required, logout_user, current_user, UserMixin
from unittest.mock import patch, MagicMock, Mock
import base64
import io
import pytest
import unittest

test_username = "test_user"
test_password = "test_password1#"


class MockUser():
    """A mock user on the wiki.
        
        This class will create a mock user object to mock the function of a user that is logged in.
        It will verify that the current user has been authenticated and is currently still logged in.
        This object will persist until the user is logged out.

        Attributes:
            username: A String containing the username of the user.
        """

    def __init__(self, username):
        """Initializes user with given username."""
        self.username = username

    def is_authenticated(self):
        """Indicates if the user is logged in or not.
        
        Returns:
            True to indicate that the user is still logged in.
        """
        return True

    def get_id(self):
        """Passes user id when called.
            
        Returns:
            The username of the mock user as their user id.
        """
        return self.username

    def get_profile_picture(self):
        """Retrieves user's profile picture.
            
        Returns:
            Link for default profile picture.
        """
        return "https://storage.cloud.google.com/awesomewikicontent/default-profile-pic.gif"


@pytest.fixture
def app():
    app = create_app({
        'TESTING': True,
    })
    return app


@pytest.fixture
def client(app):
    return app.test_client()


def test_home_page(client):
    """Tests the home page route by asserting that the home page is displayed.

    Args:
        client: Test client for the Flask app.
    """
    with patch.object(backend.Backend,
                      'get_all_page_names') as mock_get_all_page_names:
        mock_page_names = ['Page1', 'Page2', 'Page3']
        mock_get_all_page_names.return_value = mock_page_names
        with patch.object(backend.Backend,
                          'get_contributors') as get_contributors:
            get_contributors.return_value = []
            resp = client.get("/")
            assert resp.status_code == 200
            assert b'<div id="Home" style="margin-left: 20px; margin-right: 20px">' in resp.data


def test_image_gallery(client):
    """Tests if the image gallery is being displayed on the home page.

    Args:
        client: Test client for the Flask app.
    """
    with patch.object(backend.Backend,
                      'get_all_page_names') as mock_get_all_page_names:
        mock_page_names = ['Page1', 'Page2', 'Page3']
        mock_get_all_page_names.return_value = mock_page_names
        with patch.object(backend.Backend,
                          'get_contributors') as get_contributors:
            get_contributors.return_value = []
            resp = client.get("/")
            assert resp.status_code == 200
            assert b'<div class="carousel-inner">' in resp.data


def test_contributors(client):
    """Tests to see if it has the contributors on the home page.

    Args:
        client: Test client for the Flask app.
    """
    with patch.object(backend.Backend,
                      'get_all_page_names') as mock_get_all_page_names:
        mock_page_names = ['Page1', 'Page2', 'Page3']
        mock_get_all_page_names.return_value = mock_page_names
        with patch.object(backend.Backend,
                          'get_contributors') as get_contributor:
            get_contributor.return_value = []
            resp = client.get("/")
            assert resp.status_code == 200
            assert b'<div id="contributors" style="margin-left: 20px; margin-right: 20px">' in resp.data


def test_login_page(client):
    """Tests the login route by asserting that the login page is displayed.

    Args:
        client: Test client for the Flask app.
    """
    with patch.object(backend.Backend,
                      'get_all_page_names') as mock_get_all_page_names:
        mock_page_names = ['Page1', 'Page2', 'Page3']
        mock_get_all_page_names.return_value = mock_page_names
        resp = client.get('/login')
        assert resp.status_code == 200
        assert b"<div id='login-page' style='margin-left: 20px; margin-right: 20px'>" in resp.data


def test_successful_login(client):
    """Tests the successful login path by creating mock Backend and User objects and asserting that user is logged in and redirected to home page.

    Args:
        client: Test client for the Flask app.
    """
    with patch.object(backend.Backend,
                      'get_all_page_names') as mock_get_all_page_names:
        mock_page_names = ['Page1', 'Page2', 'Page3']
        mock_get_all_page_names.return_value = mock_page_names
        with patch.object(backend.Backend,
                          'get_contributors') as get_contributor:
            with patch.object(backend.Backend, 'sign_in') as mock_sign_in:
                mock_sign_in.return_value = True

                with patch('flask_login.utils._get_user') as mock_get_user:
                    mock_get_user.return_value = MockUser(test_username)

                    resp = client.post('/login',
                                       data=dict(Username=test_username,
                                                 Password=test_password),
                                       follow_redirects=True)

                    assert resp.status_code == 200
                    assert b'href="/logout"' in resp.data
                    assert current_user.is_authenticated


def test_unsuccessful_login(client):
    """Tests the unsuccessful login path by creating a mock Backend object and asserting that error flash message is displayed.

    Args:
        client: Test client for the Flask app.
    """
    with patch.object(backend.Backend,
                      'get_all_page_names') as mock_get_all_page_names:
        mock_page_names = ['Page1', 'Page2', 'Page3']
        mock_get_all_page_names.return_value = mock_page_names
        with patch.object(backend.Backend, 'sign_in') as mock_sign_in:
            mock_sign_in.return_value = False

            resp = client.post('/login',
                               data=dict(Username=test_username,
                                         Password=test_password),
                               follow_redirects=True)

            assert resp.status_code == 200
            assert b"Invalid username or password. Please try again." in resp.data


def test_logout(client):
    """Tests the logout route by creating a mock User object, logging them out, and asserting that logout page is displayed and user is no longer authenticated.

    Args:
        client: Test client for the Flask app.
    """
    with patch.object(backend.Backend,
                      'get_all_page_names') as mock_get_all_page_names:
        mock_page_names = ['Page1', 'Page2', 'Page3']
        mock_get_all_page_names.return_value = mock_page_names
        with patch.object(backend.Backend,
                          'get_contributors') as get_contributor:
            with patch.object(backend.Backend, 'sign_in') as mock_sign_in:
                mock_sign_in.return_value = True

                with patch('flask_login.utils._get_user') as mock_get_user:
                    mock_get_user.return_value = MockUser(test_username)

                    resp = client.post('/login',
                                       data=dict(Username=test_username,
                                                 Password=test_password),
                                       follow_redirects=True)

                    assert current_user.is_authenticated

                    resp = client.get('/logout')
                    assert resp.status_code == 200
                    assert b"<div id='logout-message' style='margin-left: 20px; margin-right: 20px'>" in resp.data
                    assert current_user.is_authenticated != True


def test_upload_page(client):
    """Tests the upload route by asserting that the upload page is displayed.

    Args:
        client: Test client for the Flask app.
    """
    with patch.object(backend.Backend,
                      'get_all_page_names') as mock_get_all_page_names:
        mock_page_names = ['Page1', 'Page2', 'Page3']
        mock_get_all_page_names.return_value = mock_page_names
        resp = client.get("/upload")
        assert resp.status_code == 200
        assert b"<div id='upload' style='margin-left: 20px; margin-right: 20px'>" in resp.data


def test_successful_upload(client):
    """Tests the successful upload path by creating a mock Backend object and mock File, and asserting that success flash message is displayed.

    Args:
        client: Test client for the Flask app.
    """
    with patch.object(backend.Backend,
                      'get_all_page_names') as mock_get_all_page_names:
        mock_page_names = ['Page1', 'Page2', 'Page3']
        mock_get_all_page_names.return_value = mock_page_names
        with patch.object(backend.Backend, 'upload') as mock_upload:
            mock_upload.return_value = True

            file_data = b'12345'
            file = io.BytesIO(file_data)
            file.filename = 'dummy_file.png'
            with patch('flask_login.utils._get_user') as mock_get_user:
                mock_get_user.return_value = MockUser(test_username)
                resp = client.post('/upload',
                                   data={
                                       'File name': 'dummy_file.png',
                                       'File': (file, 'dummy_file.png')
                                   },
                                   content_type='multipart/form-data',
                                   follow_redirects=True)

                assert resp.status_code == 200
                assert b"File uploaded successfully." in resp.data


def test_unsuccessful_upload(client):
    """Tests the unsuccessful upload path by creating a mock Backend object and mock File, and asserting that correct error flash message is displayed.

    Args:
        client: Test client for the Flask app.
    """
    with patch.object(backend.Backend,
                      'get_all_page_names') as mock_get_all_page_names:
        mock_page_names = ['Page1', 'Page2', 'Page3']
        mock_get_all_page_names.return_value = mock_page_names
        with patch.object(backend.Backend, 'upload') as mock_upload:
            mock_upload.return_value = False

            file_data = b'12345'
            file = io.BytesIO(file_data)
            file.filename = 'dummy_file.png'

            with patch('flask_login.utils._get_user') as mock_get_user:
                mock_get_user.return_value = MockUser(test_username)
                resp = client.post('/upload',
                                   data={
                                       'File name': 'dummy_file.png',
                                       'File': (file, 'dummy_file.png')
                                   },
                                   content_type='multipart/form-data',
                                   follow_redirects=True)

                assert resp.status_code == 200
                assert b"File name is taken." in resp.data


def test_no_file_upload(client):
    """Tests the "no file submitted" path by providing a name but no file, and asserting that correct error flash message is displayed.

    Args:
        client: Test client for the Flask app.
    """
    with patch.object(backend.Backend,
                      'get_all_page_names') as mock_get_all_page_names:
        mock_page_names = ['Page1', 'Page2', 'Page3']
        mock_get_all_page_names.return_value = mock_page_names
        resp = client.post('/upload',
                           data={
                               'File name': 'dummy_file.png',
                           },
                           content_type='multipart/form-data',
                           follow_redirects=True)

        assert resp.status_code == 200
        assert b"No file selected." in resp.data


def test_signup_page(client):
    """Tests the signup route by asserting that the signup page is displayed.

    Args:
        client: Test client for the Flask app.
    """
    with patch.object(backend.Backend,
                      'get_all_page_names') as mock_get_all_page_names:
        mock_page_names = ['Page1', 'Page2', 'Page3']
        mock_get_all_page_names.return_value = mock_page_names
        resp = client.get("/signup")
        assert resp.status_code == 200
        assert b"<div id='signup-page' style='margin-left: 20px; margin-right: 20px'>" in resp.data


def test_successful_signup(client):
    """Tests the successful signup path by creating a mock Backend object and asserting that user is logged in.

    Args:
        client: Test client for the Flask app.
    """
    with patch.object(backend.Backend,
                      'get_all_page_names') as mock_get_all_page_names:
        mock_page_names = ['Page1', 'Page2', 'Page3']
        mock_get_all_page_names.return_value = mock_page_names
        with patch.object(backend.Backend,
                          'get_contributors') as get_contributor:
            with patch.object(backend.Backend, 'sign_up') as mock_sign_up:
                mock_sign_up.return_value = True
                with patch('flask_login.utils._get_user') as mock_get_user:
                    mock_get_user.return_value = MockUser('test_user')

                    resp = client.post('/signup',
                                       data=dict(Username=test_username,
                                                 Password=test_password),
                                       follow_redirects=True)

                    assert resp.status_code == 200
                    assert b'href="/logout"' in resp.data
                    assert current_user.is_authenticated


def test_taken_username_signup(client):
    """Tests the taken username signup path by creating a mock Backend object and asserting that the correct error flash message is displayed.

    Args:
        client: Test client for the Flask app.
    """
    with patch.object(backend.Backend,
                      'get_all_page_names') as mock_get_all_page_names:
        mock_page_names = ['Page1', 'Page2', 'Page3']
        mock_get_all_page_names.return_value = mock_page_names
        with patch.object(backend.Backend, 'sign_up') as mock_sign_up:
            mock_sign_up.return_value = False

            resp = client.post('/signup',
                               data=dict(Username=test_username,
                                         Password=test_password),
                               follow_redirects=True)

            assert resp.status_code == 200
            assert b"Username already exists. Please login or choose a different username." in resp.data


def test_invalid_password_signup(client):
    """Tests the invalid password signup path by creating a mock Backend object and asserting that the correct error flash message is displayed.

    Args:
        client: Test client for the Flask app.
    """
    with patch.object(backend.Backend,
                      'get_all_page_names') as mock_get_all_page_names:
        mock_page_names = ['Page1', 'Page2', 'Page3']
        mock_get_all_page_names.return_value = mock_page_names
        resp = client.post('/signup',
                           data=dict(Username=test_username,
                                     Password="invalid_password"),
                           follow_redirects=True)

        assert resp.status_code == 200
        assert b"Your new password does not meet the requirements." in resp.data


def test_page_uploads(client):
    """Tests the pages with parameterized routes route function.

    This function mocks the 'get_wiki_page' method of the Backend class. It ensures that the dummy test page exists.

    Args:
        client: Test client for the Flask app.
    """
    with patch.object(backend.Backend,
                      'get_all_page_names') as mock_get_all_page_names:
        mock_page_names = ['Page1', 'Page2', 'Page3']
        mock_get_all_page_names.return_value = mock_page_names
        with patch.object(backend.Backend,
                          'get_wiki_page') as mock_get_wiki_page:
            mock_content = 'Test wiki page content'
            mock_get_wiki_page.return_value = mock_content

            resp = client.get('/pages/TestPage')

            assert resp.status_code == 200
            assert mock_content in resp.get_data(as_text=True)


def test_pages(client):
    """Tests the 'pages' route function. 

    This function mocks the 'get_all_page_names' method of the Backend class to return a list of mock page names.
    
    Args:
        client: Test client for the Flask app.
    """
    with patch.object(backend.Backend,
                      'get_all_page_names') as mock_get_all_page_names:
        mock_page_names = ['Page1', 'Page2', 'Page3']
        mock_get_all_page_names.return_value = mock_page_names
        with patch.object(backend.Backend,
                          'get_all_page_names') as mock_get_all_page_names:
            mock_page_names = ['Page1', 'Page2', 'Page3']
            mock_get_all_page_names.return_value = mock_page_names

            resp = client.get('/pages')

            assert resp.status_code == 200

            assert b"<div id='display-pages' style='margin-left: 20px; margin-right: 20px'>" in resp.data

            for page_name in mock_page_names:
                assert page_name in resp.get_data(as_text=True)


def test_about(client):
    """ Test the about route function.

    This function tests the behavior of the 'about' Flask route function by mocking the 'get_image' function of the Backend class using path.object().

    Args:
        client: Test client for the Flask app.
    """
    with patch.object(backend.Backend,
                      'get_all_page_names') as mock_get_all_page_names:
        mock_page_names = ['Page1', 'Page2', 'Page3']
        mock_get_all_page_names.return_value = mock_page_names
        with patch.object(backend.Backend, 'get_image') as mock_get_image:

            #Set up mock data thing

            resp = client.get('/about')

            assert resp.status_code == 200

            #check that images are present in html
            assert b"<div id='about-authors' style='margin-left: 20px; margin-right: 20px'>" in resp.data
            mock_get_image.assert_any_call('camila')
            mock_get_image.assert_any_call('sarah')
            mock_get_image.assert_any_call('ricardo')


def test_about_page_has_search_bar(client):
    '''Test function to verify that the about page has a search bar.

    Args:
        client: A Flask test client instance.
    '''
    with patch.object(backend.Backend,
                      'get_all_page_names') as mock_get_all_page_names:
        mock_page_names = ['Page1', 'Page2', 'Page3']
        mock_get_all_page_names.return_value = mock_page_names
        with patch.object(backend.Backend, 'get_image') as mock_get_image:
            mock_get_image = None
            response = client.get('/about')
            assert b'Search' in response.data


def test_home_page_has_search_bar(client):
    '''Test function to verify that the homepage has a search bar.

    Args:
        client: A Flask test client instance.
    '''
    with patch.object(backend.Backend,
                      'get_all_page_names') as mock_get_all_page_names:
        mock_page_names = ['Page1', 'Page2', 'Page3']
        mock_get_all_page_names.return_value = mock_page_names
        with patch.object(backend.Backend,
                          'get_contributors') as get_contributor:
            response = client.get('/')
            assert b'Search' in response.data


def test_pages_page_has_search_bar(client):
    '''Test function to verify that the pages page has a search bar.

    Args:
        client: A Flask test client instance.
    '''
    with patch.object(backend.Backend,
                      'get_all_page_names') as mock_get_all_page_names:
        mock_page_names = ['Page1', 'Page2', 'Page3']
        mock_get_all_page_names.return_value = mock_page_names
        with patch.object(backend.Backend,
                          'get_all_page_names') as mock_get_all_page_names:
            mock_get_all_page_names = None
            response = client.get('/pages')
            assert b'Search' in response.data


def test_uploaded_page_has_search_bar(client):
    '''Test function to verify that uploaded page has a search bar.

    Args:
        client: A Flask test client instance.
    '''
    with patch.object(backend.Backend,
                      'get_all_page_names') as mock_get_all_page_names:
        mock_page_names = ['Page1', 'Page2', 'Page3']
        mock_get_all_page_names.return_value = mock_page_names
        with patch.object(backend.Backend,
                          'get_wiki_page') as mock_get_wiki_page:
            mock_get_wiki_page = None
            response = client.get('/pages/cpu.html')
            assert b'Search' in response.data


def test_upload_page_has_search_bar(client):
    '''Test function to verify that upload page has a search bar.

    Args:
        client: A Flask test client instance.
    '''
    with patch.object(backend.Backend,
                      'get_all_page_names') as mock_get_all_page_names:
        mock_page_names = ['Page1', 'Page2', 'Page3']
        mock_get_all_page_names.return_value = mock_page_names
        response = client.get('/upload')
        assert b'Search' in response.data


def test_logout_page_has_search_bar(client):
    '''Test function to verify that the logout page has a search bar.

    Args:
        client: A Flask test client instance.
    '''
    with patch.object(backend.Backend,
                      'get_all_page_names') as mock_get_all_page_names:
        mock_page_names = ['Page1', 'Page2', 'Page3']
        mock_get_all_page_names.return_value = mock_page_names
        response = client.get('/logout')
        assert b'Search' in response.data


def test_login_page_has_search_bar(client):
    '''Test function to verify that the login page has a search bar.

    Args:
        client: A Flask test client instance.
    '''
    with patch.object(backend.Backend,
                      'get_all_page_names') as mock_get_all_page_names:
        mock_page_names = ['Page1', 'Page2', 'Page3']
        mock_get_all_page_names.return_value = mock_page_names
        response = client.get('/login')
        assert b'Search' in response.data


def test_signup_page_has_search_bar(client):
    '''Test function to verify that the signup page has a search bar.

    Args:
        client: A Flask test client instance.
    '''
    with patch.object(backend.Backend,
                      'get_all_page_names') as mock_get_all_page_names:
        mock_page_names = ['Page1', 'Page2', 'Page3']
        mock_get_all_page_names.return_value = mock_page_names
        response = client.get('/signup')
        assert b'Search' in response.data


def test_profile_page_has_search_bar(client):
    '''Test function to verify that the profile page has a search bar.

    Args:
        client: A Flask test client instance.
    '''
    with patch.object(backend.Backend,
                      'get_all_page_names') as mock_get_all_page_names:
        mock_page_names = ['Page1', 'Page2', 'Page3']
        mock_get_all_page_names.return_value = mock_page_names
        with patch.object(backend.Backend,
                          'get_profile_pic') as mock_profile_pic:
            mock_profile_pic.return_value = True
            with patch.object(backend.Backend,
                              'get_contributors') as get_contributor:
                with patch.object(backend.Backend, 'sign_in') as mock_sign_in:
                    mock_sign_in.return_value = True
                    with patch.object(backend.Backend,
                                      "get_user_files") as get_user_files:
                        get_user_files.return_value = ["file.html"]
                        with patch(
                                'flask_login.utils._get_user') as mock_get_user:
                            mock_get_user.return_value = MockUser(test_username)
                            response = client.get('/profile')
                            assert b'Search' in response.data


def test_profile_page(client):
    """Tests the profile route by asserting that the profile page is displayed.

    Args:
        client: Test client for the Flask app.
    """
    with patch.object(backend.Backend,
                      'get_all_page_names') as mock_get_all_page_names:
        mock_page_names = ['Page1', 'Page2', 'Page3']
        mock_get_all_page_names.return_value = mock_page_names
        with patch.object(backend.Backend,
                          'get_profile_pic') as mock_profile_pic:
            mock_profile_pic.return_value = True
            with patch.object(backend.Backend,
                              'get_contributors') as get_contributor:
                with patch.object(backend.Backend, 'sign_in') as mock_sign_in:
                    mock_sign_in.return_value = True
                    with patch.object(backend.Backend,
                                      "get_user_files") as get_user_files:
                        get_user_files.return_value = ["file.html"]
                        with patch(
                                'flask_login.utils._get_user') as mock_get_user:
                            mock_get_user.return_value = MockUser(test_username)

                            resp = client.post('/login',
                                               data=dict(
                                                   Username=test_username,
                                                   Password=test_password),
                                               follow_redirects=True)
                            resp = client.get("/profile")
                            assert resp.status_code == 200
                            assert b"<div id='profile-page' style='margin-left: 20px; margin-right: 20px'>" in resp.data


def test_successful_password_change(client):
    """Tests the successful password change path by creating a mock Backend object and asserting that the success flash message is displayed..

    Args:
        client: Test client for the Flask app.
    """
    with patch.object(backend.Backend, 'get_profile_pic') as mock_profile_pic:
        mock_profile_pic.return_value = True
        with patch.object(backend.Backend,
                          'get_all_page_names') as mock_get_all_page_names:
            mock_page_names = ['Page1', 'Page2', 'Page3']
            mock_get_all_page_names.return_value = mock_page_names
            with patch.object(backend.Backend,
                              'get_contributors') as get_contributor:
                with patch.object(backend.Backend, 'sign_in') as mock_sign_in:
                    mock_sign_in.return_value = True
                    with patch.object(backend.Backend,
                                      "get_user_files") as get_user_files:
                        get_user_files.return_value = ["file.html"]
                        with patch(
                                'flask_login.utils._get_user') as mock_get_user:
                            mock_get_user.return_value = MockUser(test_username)

                            resp = client.post('/login',
                                               data=dict(
                                                   Username=test_username,
                                                   Password=test_password),
                                               follow_redirects=True)

                            with patch.object(
                                    backend.Backend,
                                    'change_password') as mock_change_password:
                                mock_change_password.return_value = True

                                resp = client.post(
                                    '/change_password',
                                    data=dict(CurrentPassword='test_password1#',
                                              NewPassword='test_password2#'),
                                    follow_redirects=True)

                                assert resp.status_code == 200
                                assert b"Successfully updated password!" in resp.data


def test_same_password(client):
    """Tests the unsuccessful change password path (same password) by creating a mock Backend object and asserting that the correct error flash message is displayed.

    Args:
        client: Test client for the Flask app.
    """
    with patch.object(backend.Backend,
                      'get_all_page_names') as mock_get_all_page_names:
        mock_page_names = ['Page1', 'Page2', 'Page3']
        mock_get_all_page_names.return_value = mock_page_names
        with patch.object(backend.Backend,
                          'get_contributors') as get_contributor:
            with patch.object(backend.Backend, 'sign_in') as mock_sign_in:
                mock_sign_in.return_value = True

                with patch('flask_login.utils._get_user') as mock_get_user:
                    mock_get_user.return_value = MockUser(test_username)
                    with patch.object(backend.Backend,
                                      "get_user_files") as get_user_files:
                        get_user_files.return_value = ["file.html"]

                        resp = client.post('/login',
                                           data=dict(Username=test_username,
                                                     Password=test_password),
                                           follow_redirects=True)

                        resp = client.post('/change_password',
                                           data=dict(
                                               CurrentPassword=test_password,
                                               NewPassword=test_password),
                                           follow_redirects=True)

                        assert resp.status_code == 200
                        assert b"Passwords cannot match. Please try again." in resp.data


def test_incorrect_current_password(client):
    """Tests the unsuccessful change password path (incorrect current password) by creating a mock Backend object and asserting that the correct error flash message is displayed.

    Args:
        client: Test client for the Flask app.
    """
    with patch.object(backend.Backend,
                      'get_all_page_names') as mock_get_all_page_names:
        mock_page_names = ['Page1', 'Page2', 'Page3']
        mock_get_all_page_names.return_value = mock_page_names
        with patch.object(backend.Backend,
                          'get_profile_pic') as mock_profile_pic:
            mock_profile_pic.return_value = True
            with patch.object(backend.Backend,
                              "get_user_files") as get_user_files:
                get_user_files.return_value = ["file.html"]
                with patch.object(backend.Backend,
                                  'get_contributors') as get_contributor:
                    with patch.object(backend.Backend,
                                      'sign_in') as mock_sign_in:
                        mock_sign_in.return_value = True

                        with patch(
                                'flask_login.utils._get_user') as mock_get_user:
                            mock_get_user.return_value = MockUser(test_username)

                            resp = client.post('/login',
                                               data=dict(
                                                   Username=test_username,
                                                   Password=test_password),
                                               follow_redirects=True)
                            with patch.object(
                                    backend.Backend,
                                    'change_password') as mock_change_password:
                                mock_change_password.return_value = False
                                resp = client.post(
                                    '/change_password',
                                    data=dict(
                                        CurrentPassword='incorrect_password1#',
                                        NewPassword=test_password),
                                    follow_redirects=True)

                                assert resp.status_code == 200
                                assert b"Incorrect current password. Please try again." in resp.data


def test_invalid_new_password(client):
    """Tests the unsuccessful change password path (invalid new password) by creating a mock Backend object and asserting that the correct error flash message is displayed.

    Args:
        client: Test client for the Flask app.
    """
    with patch.object(backend.Backend,
                      'get_all_page_names') as mock_get_all_page_names:
        mock_page_names = ['Page1', 'Page2', 'Page3']
        mock_get_all_page_names.return_value = mock_page_names
        with patch.object(backend.Backend,
                          'get_profile_pic') as mock_profile_pic:
            mock_profile_pic.return_value = True
            with patch.object(backend.Backend,
                              "get_user_files") as get_user_files:
                get_user_files.return_value = ["file.html"]
                with patch.object(backend.Backend,
                                  'get_contributors') as get_contributor:
                    with patch.object(backend.Backend,
                                      'sign_in') as mock_sign_in:
                        mock_sign_in.return_value = True

                        with patch(
                                'flask_login.utils._get_user') as mock_get_user:
                            mock_get_user.return_value = MockUser(test_username)

                            resp = client.post('/login',
                                               data=dict(
                                                   Username=test_username,
                                                   Password=test_password),
                                               follow_redirects=True)

                            with patch.object(
                                    backend.Backend,
                                    'change_password') as mock_change_password:
                                mock_change_password.return_value = False

                                resp = client.post(
                                    '/change_password',
                                    data=dict(CurrentPassword=test_password,
                                              NewPassword='invalid_password'),
                                    follow_redirects=True)

                                assert resp.status_code == 200
                                assert b"Your new password does not meet the requirements." in resp.data


def test_autocomplete(client):
    '''Test function to verify the functionality of autocomplete feature.

    Args:
        client: A Flask test client instance.
    '''
    with patch.object(backend.Backend,
                      'get_all_page_names') as mock_get_all_page_names:
        mock_page_names = ['Page1', 'Page2', 'Page3']
        mock_get_all_page_names.return_value = mock_page_names
        with patch.object(backend.Backend,
                          'get_contributors') as get_contributor:
            search_value = "CPU"

            resp = client.post("/",
                               data=dict(search_value=search_value),
                               follow_redirects=True)

            assert resp.status_code == 200
            assert b"<datalist id=\"list-pcparts\">" in resp.data
            assert b'<div id="autocompleteDropdown">' in resp.data


def test_search_page(client):
    """Tests the search-results route by asserting that the search page displays matching results.

    Args:
        client: A Flask test client instance.
    """
    with patch.object(backend.Backend,
                      'get_all_page_names') as mock_get_all_page_names:
        mock_page_names = ['Page1', 'Page2', 'Page3']
        mock_get_all_page_names.return_value = mock_page_names
        resp = client.post(
            '/search-results',
            data=dict(
                SearchInput='p',
                MatchingResults='"psu.html,peripherals.html,pc-basics.html"'),
            follow_redirects=True)
        assert resp.status_code == 200
        assert b"<div id='search-results' style='margin-left: 20px; margin-right: 20px'>" in resp.data
        assert b"psu.html" in resp.data
        assert b"peripherals.html" in resp.data
        assert b"pc-basics.html" in resp.data


def test_successful_upload_profile_picture(client):
    """Tests the successful upload profile picture path by creating a mock Backend object and asserting that the success flash message is displayed.

    Args:
        client: Test client for the Flask app.
    """
    with patch.object(backend.Backend,
                      'get_all_page_names') as mock_get_all_page_names:
        mock_page_names = ['Page1', 'Page2', 'Page3']
        mock_get_all_page_names.return_value = mock_page_names
        with patch.object(backend.Backend,
                          'get_profile_pic') as mock_profile_pic:
            mock_profile_pic.return_value = True
            with patch.object(backend.Backend,
                              "get_user_files") as get_user_files:
                get_user_files.return_value = ["file.html"]
                with patch.object(backend.Backend,
                                  'get_contributors') as get_contributor:
                    with patch.object(backend.Backend,
                                      'sign_in') as mock_sign_in:
                        mock_sign_in.return_value = True
                        with patch(
                                'flask_login.utils._get_user') as mock_get_user:
                            mock_get_user.return_value = MockUser(test_username)
                            with patch.object(backend.Backend,
                                              'change_profile_picture'
                                             ) as mock_change_profile_picture:
                                mock_change_profile_picture.return_value = True

                                file_data = b'12345'
                                file = io.BytesIO(file_data)
                                file.filename = 'dummy_file.png'

                                resp = client.post(
                                    '/upload-pfp',
                                    data={'File': (file, 'dummy_file.png')},
                                    content_type='multipart/form-data',
                                    follow_redirects=True)

                                assert resp.status_code == 200
                                assert b"Successfully updated profile picture." in resp.data


def test_incorrect_filetype_upload_profile_picture(client):
    """Tests the unsuccessful upload profile picture path (incorrect file type) by creating a mock Backend object and asserting that the correct error flash message is displayed.

    Args:
        client: Test client for the Flask app.
    """
    with patch.object(backend.Backend,
                      'get_all_page_names') as mock_get_all_page_names:
        mock_page_names = ['Page1', 'Page2', 'Page3']
        mock_get_all_page_names.return_value = mock_page_names
        with patch.object(backend.Backend,
                          'get_profile_pic') as mock_profile_pic:
            mock_profile_pic.return_value = True
            with patch.object(backend.Backend,
                              "get_user_files") as get_user_files:
                get_user_files.return_value = ["file.html"]
                with patch.object(backend.Backend,
                                  'get_contributors') as get_contributor:
                    with patch.object(backend.Backend,
                                      'sign_in') as mock_sign_in:
                        mock_sign_in.return_value = True
                        with patch(
                                'flask_login.utils._get_user') as mock_get_user:
                            mock_get_user.return_value = MockUser(test_username)
                            with patch.object(backend.Backend,
                                              'change_profile_picture'
                                             ) as mock_change_profile_picture:
                                mock_change_profile_picture.return_value = False

                                file_data = b'12345'
                                file = io.BytesIO(file_data)
                                file.filename = 'dummy_file.html'

                                resp = client.post(
                                    '/upload-pfp',
                                    data={'File': (file, 'dummy_file.html')},
                                    content_type='multipart/form-data',
                                    follow_redirects=True)

                                assert resp.status_code == 200
                                assert b"Could not update profile picture." in resp.data


def test_no_file_upload_profile_picture(client):
    """Tests the unsuccessful upload profile picture path (no file) by creating a mock Backend object and asserting that the correct error flash message is displayed.

    Args:
        client: Test client for the Flask app.
    """
    with patch.object(backend.Backend,
                      'get_all_page_names') as mock_get_all_page_names:
        mock_page_names = ['Page1', 'Page2', 'Page3']
        mock_get_all_page_names.return_value = mock_page_names
        with patch.object(backend.Backend,
                          'get_profile_pic') as mock_profile_pic:
            mock_profile_pic.return_value = True
            with patch.object(backend.Backend,
                              "get_user_files") as get_user_files:
                get_user_files.return_value = ["file.html"]
                with patch.object(backend.Backend,
                                  'get_contributors') as get_contributor:
                    with patch.object(backend.Backend,
                                      'sign_in') as mock_sign_in:
                        mock_sign_in.return_value = True
                        with patch(
                                'flask_login.utils._get_user') as mock_get_user:
                            mock_get_user.return_value = MockUser(test_username)

                            resp = client.post(
                                '/upload-pfp',
                                data={
                                    'File name': 'dummy_file.png',
                                },
                                content_type='multipart/form-data',
                                follow_redirects=True)

                            assert resp.status_code == 200
                            assert b"No file selected." in resp.data


def test_remove_profile_picture(client):
    """Tests the remove profile picture path by creating a mock Backend object and asserting that the success flash message is displayed.

    Args:
        client: Test client for the Flask app.
    """
    with patch.object(backend.Backend,
                      'get_all_page_names') as mock_get_all_page_names:
        mock_page_names = ['Page1', 'Page2', 'Page3']
        mock_get_all_page_names.return_value = mock_page_names
        with patch.object(backend.Backend,
                          'get_profile_pic') as mock_profile_pic:
            mock_profile_pic.return_value = True
            with patch.object(backend.Backend,
                              "get_user_files") as get_user_files:
                get_user_files.return_value = ["file.html"]
                with patch.object(backend.Backend,
                                  'get_contributors') as get_contributor:
                    with patch.object(backend.Backend,
                                      'sign_in') as mock_sign_in:
                        mock_sign_in.return_value = True

                        with patch(
                                'flask_login.utils._get_user') as mock_get_user:
                            mock_get_user.return_value = MockUser(test_username)
                            with patch.object(backend.Backend,
                                              'change_profile_picture'
                                             ) as mock_change_profile_picture:
                                mock_change_profile_picture.return_value = True

                                file_data = b'12345'
                                file = io.BytesIO(file_data)
                                file.filename = 'dummy_file.png'

                                resp = client.post('/remove-pfp')

                                assert resp.status_code == 200
                                assert b"Successfully removed profile picture." in resp.data


def test_submit_reply(client):
    '''Test the submission of a reply by sending a POST request to the '/submit_reply' endpoint.
    
    Args:
        client: A Flask client object for making requests to the application.
    '''
    with patch.object(backend.Backend,
                      'get_all_page_names') as mock_get_all_page_names:
        mock_page_names = ['Page1', 'Page2', 'Page3']
        mock_get_all_page_names.return_value = mock_page_names
        with patch.object(backend.Backend, 'get_faq') as get_faq:
            with patch.object(backend.Backend, 'submit_reply') as submit_reply:
                with patch('flask_login.utils._get_user') as mock_get_user:
                    mock_get_user.return_value = MockUser('test_user')
                    resp = client.post('/submit_reply',
                                       data={
                                           'reply': 'testing',
                                           'index': 0
                                       })
                    assert resp.status_code == 200
                    assert b"Successfully submitted reply." in resp.data


def test_submit_question(client):
    '''Test the functionality of the submit_question endpoint when a user is logged in.

    Mocks the get_all_page_names, get_faq, submit_question, and _get_user methods.
    Sends a POST request to /submit_question with the data {'question': 'test'}.
    Asserts that the response has a status code of 200 and contains the success message.

    Args:
        client: A Flask client for making requests to the application.
    '''

    with patch.object(backend.Backend,
                      'get_all_page_names') as mock_get_all_page_names:
        mock_page_names = ['Page1', 'Page2', 'Page3']
        mock_get_all_page_names.return_value = mock_page_names
        with patch.object(backend.Backend, 'get_faq') as get_faq:
            with patch.object(backend.Backend,
                              'submit_question') as submit_question:
                with patch('flask_login.utils._get_user') as mock_get_user:
                    mock_get_user.return_value = MockUser('test_user')
                    resp = client.post('/submit_question',
                                       data={'question': 'test'})
                    assert resp.status_code == 200
                    assert b"Successfully submitted question." in resp.data


def test_faq_page_logged_in(client):
    """Test the FAQ page when a user is logged in.

    The function patches the Backend class's get_all_page_names and get_faq methods to provide mock data, then patches
    the _get_user utility function from Flask-Login to simulate a logged-in user. The function then sends a GET request
    to the /FAQ route and asserts that the response contains the expected HTML elements for the reply and question forms,
    as well as the test question in the FAQ data.

    Args:
        client: A Flask client for making requests to the application.
    """
    with patch.object(backend.Backend,
                      'get_all_page_names') as mock_get_all_page_names:
        mock_page_names = ['Page1', 'Page2', 'Page3']
        mock_get_all_page_names.return_value = mock_page_names
        with patch.object(backend.Backend, 'get_faq') as get_faq:
            get_faq.return_value = test_faq = [{
                "text": "test question?",
                "user": test_username,
                "replies": []
            }]
            with patch('flask_login.utils._get_user') as mock_get_user:
                mock_get_user.return_value = MockUser('test_user')
                resp = client.post('/FAQ')
                assert resp.status_code == 200
                assert b"<div id='reply-form'>" in resp.data
                assert b"<div id='question-form'>" in resp.data
                assert b"test question?" in resp.data


def test_faq_page_logged_out(client):
    '''Tests the behavior of the FAQ page when the user is logged out.

    The function mocks the Backend class's `get_all_page_names()` method to return mock page names, and the `get_faq()`
    method to return a test FAQ object. It then sends a POST request to the '/FAQ' endpoint and asserts that the
    response status code is 200, that the reply-form and question-form are not present in the response data, and that
    the test question is present in the response data.

    Args:
        client: A test client for making requests to the Flask application.
    '''
    with patch.object(backend.Backend,
                      'get_all_page_names') as mock_get_all_page_names:
        mock_page_names = ['Page1', 'Page2', 'Page3']
        mock_get_all_page_names.return_value = mock_page_names
        with patch.object(backend.Backend, 'get_faq') as get_faq:
            get_faq.return_value = test_faq = [{
                "text": "test question?",
                "user": test_username,
                "replies": []
            }]
            resp = client.post('/FAQ')
            assert resp.status_code == 200
            assert b"<div id='reply-form'>" not in resp.data
            assert b"<div id='question-form'>" not in resp.data
            assert b"test question?" in resp.data
