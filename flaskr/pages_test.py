from flaskr import create_app
from flask import url_for
from flask import Flask
import base64

import pytest

# See https://flask.palletsprojects.com/en/2.2.x/testing/ 
# for more info on testing
@pytest.fixture
def app():
    app = create_app({
        'TESTING': True,
    })
    return app

@pytest.fixture
def client(app):
    return app.test_client()


# TODO(Checkpoint (groups of 4 only) Requirement 4): Change test to
# match the changes made in the other Checkpoint Requirements.
def test_home_page(client):
    resp = client.get("/")
    assert resp.status_code == 200
    assert b"<button>Home</button>" in resp.data
    assert b"<button>About</button>" in resp.data
    assert b"<button>Pages</button>" in resp.data
    assert b"<span>   |   </span>" in resp.data
    assert b"<button>Log In</button>" in resp.data
    assert b"<button>Sign Up</button>" in resp.data
    assert b"<span>Welcome to our awesome Wiki Server, we're glad to have you here!</span>" in resp.data
    assert b"<br><font size= 5><b>The Ultimate Guide to Building a PC</b></font>" in resp.data

# TODO(Project 1): Write tests for other routes.
def test_pages(client):
    resp = client.get("/pages")
    assert resp.status_code == 200

def create_app():
    app = Flask(__name__)
    app.config['Wiki_Server'] = 'https://8080-cs-724233522011-default.cs-us-central1-pits.cloudshell.dev/'

def test_about(client, app):
    with app.app_context():
        response = client.get(url_for('about'))
        assert response.status_code == 200
        assert b'<title>About<title>' in response.data
        assert b'<h1>About Us</h1>' in response.data
        image_names = ["camila", "sarah", "ricardo"]
        image_datas = be.get_image(image_names)
        image_data = [base64.b64encode(image).decode('utf-8') for image in image_datas]
        for data in image_data:
            assert bytes(data, 'utf-8') in response.data

    

