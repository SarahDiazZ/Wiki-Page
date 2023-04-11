from flaskr.backend import Backend
from unittest.mock import MagicMock
import pytest

# TODO(Project 1): Write tests for Backend methods.


def test_get_wiki_page():
    """Tests if the get_wiki_page returns the content that is inside of the file."""
    content = "<div>testing</div>"
    be = Backend()

    blob1 = MagicMock()
    blob1.download_as_string().decode.return_value = content
    be.content_bucket = MagicMock()
    be.content_bucket.get_blob.return_value = blob1

    assert be.get_wiki_page("testing") == content


def test_get_all_page_names():
    """Verifies if only the html files are being returned."""
    html_file = "testing.html"
    wrong_file = "testing.jpg"
    be = Backend()

    blob1 = MagicMock()
    blob2 = MagicMock()
    blob1.name = html_file
    blob2.name = wrong_file
    be.content_bucket = MagicMock()
    be.content_bucket.list_blobs.return_value = [blob1, blob2]

    assert be.get_all_page_names() == [html_file]


def test_upload_success():
    """Tests if the upload was successful with no conflict."""
    be = Backend()

    file = MagicMock()
    file.filename.return_value = "testing.html"
    blob1 = MagicMock()
    blob1.upload_from_file.return_value = MagicMock()
    blob1.exists.return_value = False
    be.content_bucket = MagicMock()
    be.content_bucket.blob.return_value = blob1

    assert be.upload("testing", file) == True


def test_upload_fail():
    """Tests if the upload fails when a file with the same name already exists."""
    be = Backend()

    file = MagicMock()
    file.filename = "testing.html"
    blob1 = MagicMock()
    blob1.exists.return_value = True
    be.content_bucket = MagicMock()
    be.content_bucket.blob.return_value = blob1

    assert be.upload("testing", file) == False


def test_sign_up_success():
    """Tests the sign up was successful and there is no username that is taken."""
    be = Backend()

    blob1 = MagicMock()
    blob1.exists.return_value = False
    be.password_bucket = MagicMock()
    be.password_bucket.blob.return_value = blob1

    assert be.sign_up("user", "password") == True


def test_sign_up_fail():
    """Tests if the sign up was not possible because the username is taken."""
    be = Backend()

    blob1 = MagicMock()
    blob1.exists.return_value = True
    be.password_bucket = MagicMock()
    be.password_bucket.blob.return_value = blob1

    assert be.sign_up("user", "password") == False


def test_sign_in_success():
    """Tests if the sign in was successful, username exists and the password matches."""
    correct = "password"
    be = Backend()

    blob3 = MagicMock()
    blob3.return_value = True
    blob3.download_as_string().decode.return_value = correct
    be.password_bucket = MagicMock()
    be.password_bucket.get_blob.return_value = blob3

    assert be.sign_in("user", correct) == True


def test_sign_in_fail_does_not_exist():
    """Tests if the sign in was not possible because the username does not exists."""
    correct = "password"
    be = Backend()

    blob1 = MagicMock()
    blob1.returns = False
    be.password_bucket = MagicMock()
    be.password_bucket.get_blob.return_value = blob1

    assert be.sign_in("user", correct) == False


def test_sign_in_fail_match():
    """Tests if the sign in username exists, but the password does not match."""
    incorrect = "passwor"
    correct = "password"
    be = Backend()

    blob1 = MagicMock()
    blob1.return_value = True
    blob1.download_as_string.decode.return_value = incorrect
    be.password_bucket = MagicMock()
    be.password_bucket.get_blob.return_value = blob1

    assert be.sign_in("user", correct) == False


def test_get_image():
    """Tests getting an image from Google Cloud."""
    be = Backend()

    img = "testing.jpg"
    blob1 = MagicMock()
    blob1.name = img
    be.content_bucket = MagicMock()
    be.content_bucket.get_blob.return_value = blob1

    assert be.get_image(img) == f"awesomewikicontent/{img}"
