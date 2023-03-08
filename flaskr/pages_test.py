from flaskr import create_app
from flask import Flask

from app import login

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

    
