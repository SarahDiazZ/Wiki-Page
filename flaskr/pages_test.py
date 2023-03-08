from flaskr import create_app
from flask import url_for
from flask import Flask
from flaskr import backend
from flask_login import LoginManager, login_user, login_required, logout_user, current_user, UserMixin
from unittest.mock import patch
import base64
import io
import pytest

# See https://flask.palletsprojects.com/en/2.2.x/testing/ 
# for more info on testing

class MockUser:
    def __init__(self, username):
        self.username = username

    def is_authenticated(self):
        return True

    def is_active(self):
        return True

    def get_id(self):
        return self.username

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
    resp = client.get("/")
    assert resp.status_code == 200
    assert b"<div id='navigation-buttons'>" in resp.data

def test_login_page(client):
    resp = client.get('/login')
    assert resp.status_code == 200
    assert b"<div id='login-page'>" in resp.data

def test_valid_login(client):
    with patch.object(backend.Backend, 'sign_in') as mock_sign_in:
        mock_sign_in.return_value = True

        with patch('flask_login.utils._get_user') as mock_get_user:
            mock_get_user.return_value = MockUser('test_user')

            resp = client.post('/login', data=dict(
                Username='test_user',
                Password='test_password'
            ), follow_redirects=True)

            assert resp.status_code == 200
            assert b"<div id='navigation-buttons'>" in resp.data
            assert mock_sign_in.called
            assert current_user.is_authenticated

def test_invalid_login(client):
    with patch.object(backend.Backend, 'sign_in') as mock_sign_in:
        mock_sign_in.return_value = False

        resp = client.post('/login', data=dict(
            Username='test_user',
            Password='test_password'
        ), follow_redirects=True)

        assert resp.status_code == 200
        assert b"Invalid username or password. Please try again." in resp.data
        assert mock_sign_in.called

def test_logout(client):
    with patch('flask_login.utils._get_user') as mock_get_user:
        mock_get_user.return_value = MockUser('test_user')

        resp = client.post('/login', data=dict(
            Username='test_user',
            Password='test_password'
        ), follow_redirects=True)

        assert current_user.is_authenticated

        resp = client.get('/logout')
        assert resp.status_code == 200
        assert b"<div id='logout-message'>" in resp.data
        assert current_user.is_authenticated != True

def test_upload_page(client):
    resp = client.get("/upload")
    assert resp.status_code == 200
    assert b"<div id='upload'>" in resp.data

def test_successful_upload(client):
    with patch.object(backend.Backend, 'upload') as mock_upload:
        mock_upload.return_value = True
        
        file_data = b'12345'
        file = io.BytesIO(file_data)
        file.filename = 'dummy_file.png'

        resp = client.post('/upload', data={
            'File name': 'dummy_file.png',
            'File': (file, 'dummy_file.png')
        }, content_type='multipart/form-data', follow_redirects=True)

        assert resp.status_code == 200
        assert b"File uploaded successfully." in resp.data

def test_unsuccessful_upload(client):
    with patch.object(backend.Backend, 'upload') as mock_upload:
        mock_upload.return_value = False
        
        file_data = b'12345'
        file = io.BytesIO(file_data)
        file.filename = 'dummy_file.png'

        resp = client.post('/upload', data={
            'File name': 'dummy_file.png',
            'File': (file, 'dummy_file.png')
        }, content_type='multipart/form-data', follow_redirects=True)

        assert resp.status_code == 200
        assert b"File name is taken." in resp.data

def test_no_file_upload(client):
    resp = client.post('/upload', data={
            'File name': 'dummy_file.png',
        }, content_type='multipart/form-data', follow_redirects=True)

    assert resp.status_code == 200
    assert b"No file selected." in resp.data

def test_page_uploads(client):
    with patch.object(backend.Backend, 'get_wiki_page') as mock_get_wiki_page:
        #Set the return value of the mock method
        mock_content = 'Test wiki page content'
        mock_get_wiki_page.return_value = mock_content

        #Make a GET request to the test URL
        resp = client.get('/pages/TestPage')

        #check that the response status code is 200
        assert resp.status_code == 200
        
        #Check that the rendered HTML contains the mock content
        assert mock_content in resp.get_data(as_text=True)

        #Only reason it's navigation-buttons is because in the inspect the id is navigation-buttons
        assert b"<div id='navigation-buttons'>" in resp.data

def test_pages(client):
    #Mock the get_all_page_names method of the Backend class
    with patch.object(backend.Backend, 'get_all_page_names') as mock_get_all_page_names:
        #Set the return value of the mock method
        mock_page_names = ['Page1', 'Page2', 'Page3']
        mock_get_all_page_names.return_value = mock_page_names

        #Make a GET request to the test URL
        resp = client.get('/pages')

        #Check that the response status code is 200
        assert resp.status_code == 200

        assert b"<div id='display-pages'>" in resp.data

        #Check that the rendered HTML contains the mock page names
        for page_name in mock_page_names:
            assert page_name in resp.get_data(as_text=True)

def test_about(client):
    # image_names = ["camila", "sarah", "ricardo"]
    with patch.object(backend.Backend, 'get_image') as mock_get_image:
        mock_get_image.return_value = [b'image_data_1', b'image_data_2', b'image_data_3']

        resp = client.get("/about")
    assert resp.status_code == 200

    assert b'base64_image_data_1' in resp.data
    assert b'base64_image_data_2' in resp.data
    assert b'base64_image_data_3' in resp.data

