from flaskr import create_app
from flask import url_for
from flask import Flask
import base64
from unittest.mock import patch
from flaskr import backend

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

# TODO(Project 1): Write tests for other routes.
# def test_pages(client):
#     resp = client.get("/pages")
#     assert resp.status_code == 200