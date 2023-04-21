from flaskr.backend import Backend
from unittest.mock import patch, MagicMock
import pytest
import json


def test_get_wiki_page():
    """Tests if the get_wiki_page returns the content that is inside of the file."""
    content = "<div>testing</div>"
    be = Backend()

    blob1 = MagicMock()
    blob1.download_as_bytes().decode.return_value = content
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

    json_test_data = {
        "user": {
            "profile_pic": "default-profile-pic.gif",
            "files_uploaded": ["file.html"]
        }
    }
    json_test_data_str = '{"testing": {"profile_pic": "default-profile-pic.gif", "files_uploaded": ["file.html"]}'

    expected = {
        "user": {
            "profile_pic": "default-profile-pic.gif",
            "files_uploaded": ["file.html", "testing.html"]
        }
    }

    file = MagicMock()
    file.filename = "test.html"

    blob = MagicMock()
    blob.exists.return_value = False
    blob.upload_from_file.return_value = None
    be.content_bucket = MagicMock()
    be.content_bucket.blob.return_value = blob

    json_blob = MagicMock()
    json_blob.download_as_bytes.decode.return_value = json_test_data_str
    json_blob.upload_from_string.return_value = None

    with patch('json.loads', new_callable=MagicMock) as mock_load, patch(
            'json.dumps', new_callable=MagicMock) as mock_dump:
        mock_dump.return_value = json_test_data_str
        mock_load.return_value = json_test_data
        assert be.upload("user", "testing", file) == True
        assert json_test_data == expected


def test_upload_fail():
    """Tests if the upload fails when a file with the same name already exists."""
    be = Backend()

    json_test_data = {
        "user": {
            "profile_pic": "default-profile-pic.gif",
            "files_uploaded": ["file.html"]
        }
    }

    file = MagicMock()
    file.filename = "testing.html"
    blob1 = MagicMock()
    blob1.exists.return_value = True
    be.content_bucket = MagicMock()
    be.content_bucket.blob.return_value = blob1

    assert be.upload("user", "testing", file) == False


def test_sign_up_success():
    """Tests the sign up was successful and there is no username that is taken."""
    be = Backend()

    json_test_data = {}
    json_test_data_str = "{}"
    expected = {
        "user": {
            "profile_pic": "default-profile-pic.gif",
            "files_uploaded": []
        }
    }

    blob = MagicMock()
    blob.exists.return_value = False
    be.password_bucket = MagicMock()
    be.password_bucket.blob.return_value = blob

    json_blob = MagicMock()
    json_blob.download_as_bytes.decode.return_value = json_test_data_str
    json_blob.upload_from_string.return_value = None
    be.content_bucket = MagicMock()
    be.content_bucket.get_blob.return_value = json_blob

    with patch('random.randint', new_callable=MagicMock) as mock_randint, patch(
            'json.loads', new_callable=MagicMock) as mock_load, patch(
                'json.dumps', new_callable=MagicMock) as mock_dump:
        mock_randint.return_value = 10
        mock_dump.return_value = json_test_data_str
        mock_load.return_value = json_test_data

        assert be.sign_up("user", "password") == True
        assert json_test_data == expected


def test_sign_up_success_easter_egg():
    """Tests the sign up was successful and there is no username that is taken."""
    be = Backend()

    json_test_data = {}
    json_test_data_str = "{}"
    expected = {
        "user": {
            "profile_pic": "default-profile-pic2.gif",
            "files_uploaded": []
        }
    }

    blob = MagicMock()
    blob.exists.return_value = False
    be.password_bucket = MagicMock()
    be.password_bucket.blob.return_value = blob

    json_blob = MagicMock()
    json_blob.download_as_bytes.decode.return_value = json_test_data_str
    json_blob.upload_from_string.return_value = None
    be.content_bucket = MagicMock()
    be.content_bucket.get_blob.return_value = json_blob

    with patch('random.randint', new_callable=MagicMock) as mock_randint, patch(
            'json.loads', new_callable=MagicMock) as mock_load, patch(
                'json.dumps', new_callable=MagicMock) as mock_dump:
        mock_randint.return_value = 2
        mock_dump.return_value = json_test_data_str
        mock_load.return_value = json_test_data

        assert be.sign_up("user", "password") == True
        assert json_test_data == expected


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
    blob3.download_as_bytes().decode.return_value = correct
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


def test_successful_change_username():
    """Tests if changing the username for the user is successful when the new username is not taken."""
    be = Backend()
    expected = True
    json_test_data = {
        "testing": {
            "profile_pic": "default-profile-pic.gif",
            "files_uploaded": ["file.html", "file2.html"]
        }
    }
    json_test_data_str = '{"testing": {"profile_pic": "default-profile-pic.gif", "files_uploaded": ["file.html", "file2.html"]}'

    blob = MagicMock()
    blob.exists.return_value = False
    be.password_bucket = MagicMock()
    be.password_bucket.blob.return_value = blob

    json_blob = MagicMock()
    json_blob.download_as_bytes.decode.return_value = json_test_data_str
    json_blob.upload_from_string.return_value = None
    be.content_bucket = MagicMock()
    be.content_bucket.get_blob.return_value = json_blob

    old_user_blob = MagicMock()
    old_user_blob.delete.return_value = None
    be.password_bucket.get_blob.return_value = old_user_blob
    be.password_bucket.copy_blob.return_value = None

    with patch('json.loads', new_callable=MagicMock) as mock_load, patch(
            'json.dumps', new_callable=MagicMock) as mock_dump:
        mock_dump.return_value = json_test_data_str
        mock_load.return_value = json_test_data
        assert be.change_username("testing", "testing1") == expected
        assert "testing1" in json_test_data
        assert "testing" not in json_test_data


def test_unsuccessful_change_username():
    """Tests if changing a username for the user fails when the username is taken."""
    be = Backend()
    expected = False
    json_test_data = {
        "testing": {
            "profile_pic": "default-profile-pic.gif",
            "files_uploaded": ["file.html", "file2.html"]
        },
        "testing1": {
            "profile_pic": "default-profile-pic.gif",
            "files_uploaded": ["file3.html"]
        }
    }

    blob = MagicMock()
    blob.exists.return_value = True
    be.password_bucket = MagicMock()
    be.password_bucket.blob.return_value = blob

    assert be.change_username("testing", "testing1") == expected


def test_get_user_files():
    """Tests retrieving all the files that were uploaded by the user."""
    be = Backend()

    json_test_data = {
        "testing": {
            "profile_pic": "default-profile-pic.gif",
            "files_uploaded": ["file.html", "file2.html"]
        }
    }
    json_test_data_str = '{"testing": {"profile_pic": "default-profile-pic.gif", "files_uploaded": ["file.html", "file2.html"]}'
    expected = ["file.html", "file2.html"]

    json_blob = MagicMock()
    json_blob.download_as_bytes.decode.return_value = json_test_data_str
    be.content_bucket = json_blob

    with patch('json.loads', new_callable=MagicMock) as mock_load:
        mock_load.return_value = json_test_data
        assert be.get_user_files("testing") == expected


def test_delete_uploaded_file():
    """Tests deleting an uploaded file from the user."""
    be = Backend()

    json_test_data = {
        "testing": {
            "profile_pic": "default-profile-pic.gif",
            "files_uploaded": ["file.html"]
        }
    }
    json_test_data_str = '{"testing": {"profile_pic": "default-profile-pic.gif", "files_uploaded": ["file.html"]}}'
    expected = []

    blob = MagicMock()
    blob.remove.return_value = None
    be.content_bucket = blob

    json_blob = MagicMock()
    json_blob.download_as_bytes.decode.return_value = json_test_data_str
    json_blob.upload_from_string.return_value = MagicMock()
    be.content_bucket.get_blob.return_value = json_blob

    with patch('json.loads', new_callable=MagicMock) as mock_load, patch(
            'json.dumps', new_callable=MagicMock) as mock_dump:
        mock_dump.return_value = json_test_data_str
        mock_load.return_value = json_test_data
        assert be.delete_uploaded_file("testing", "file.html") == expected


def test_get_contributors():
    """Tests the get_contributors method in the backend and see if it is retrieving the correct data."""
    be = Backend()
    blob1 = MagicMock()
    json_test_data = {
        "testing": {
            "profile_pic": "default-profile-pic.gif",
            "files_uploaded": ["file.html"]
        }
    }
    expected = ["testing"]
    blob1.download_as_bytes.decode.return_value = '{"testing": {"profile_pic": "default-profile-pic.gif", "files_uploaded": ["file.html"]}}'

    be.content_bucket = MagicMock()
    be.content_bucket.get_blob.return_value = blob1

    with patch('json.loads', new_callable=MagicMock) as mock_load:
        mock_load.return_value = json_test_data
        assert be.get_contributors() == expected


def test_get_profile_pic():
    '''
    '''
    be = Backend()

    json_data = {
        "user1": {
            "profile_pic": "profile1.jpg"
        },
        "user2": {
            "profile_pic": "profile2.jpg"
        }
    }

    blob1 = MagicMock()
    blob1.download_as_bytes.decode.return_value = json_data

    be.content_bucket = MagicMock()
    be.content_bucket.get_blob.return_value = blob1
    with patch('json.loads', new_callable=MagicMock) as mock_load:
        mock_load.return_value = json_data
        assert be.get_profile_pic("user1") == "profile1.jpg"


def test_change_password_success():
    """
    """
    be = Backend()
    blob = MagicMock()
    blob.return_value = True
    blob.download_as_string().decode.return_value = "password"
    be.password_bucket = MagicMock()
    be.password_bucket.get_blob.return_value = blob

    assert be.change_password("test_user", "password", "new_password") == True


def test_change_password_fail():
    """
    """
    be = Backend()
    blob = MagicMock()
    blob.return_value = True
    blob.download_as_string().decode.return_value = "password"
    be.password_bucket = MagicMock()
    be.password_bucket.get_blob.return_value = blob

    assert be.change_password("test_user", "wrong_password",
                              "new_password") == False


def test_change_profile_picture_success():
    """
    """
    be = Backend()
    new_pfp = MagicMock()
    new_pfp.filename.split.return_value = ["new_pfp", "png"]

    json_test_data = {
        "test_user": {
            "profile_pic": "default-profile-pic.gif",
            "files_uploaded": []
        }
    }

    expected = {
        "test_user": {
            "profile_pic":
                "test_user-profile-picture-superduperteamawesome.png",
            "files_uploaded": []
        }
    }

    blob = MagicMock()
    blob.download_as_bytes.decode.return_value = json_test_data

    be.content_bucket = MagicMock()
    be.content_bucket.get_blob.return_value = blob

    with patch('json.loads', new_callable=MagicMock) as mock_load:
        mock_load.return_value = json_test_data
        assert be.change_profile_picture("test_user", new_pfp, False) == True
        assert json_test_data == expected


def test_change_profile_picture_fail():
    """
    """
    be = Backend()
    new_pfp = MagicMock()
    new_pfp.filename.split.return_value = ["new_pfp", "html"]

    json_test_data = {
        "test_user": {
            "profile_pic": "default-profile-pic.gif",
            "files_uploaded": []
        }
    }

    expected = {
        "test_user": {
            "profile_pic": "default-profile-pic.gif",
            "files_uploaded": []
        }
    }

    blob = MagicMock()
    blob.download_as_bytes.decode.return_value = json_test_data

    be.content_bucket = MagicMock()
    be.content_bucket.get_blob.return_value = blob

    with patch('json.loads', new_callable=MagicMock) as mock_load:
        mock_load.return_value = json_test_data
        assert be.change_profile_picture("test_user", new_pfp, False) == False
        assert json_test_data == expected


def test_remove_profile_picture():
    """
    """
    be = Backend()

    json_test_data = {
        "test_user": {
            "profile_pic": "test_pfp.png",
            "files_uploaded": []
        }
    }

    expected = {
        "test_user": {
            "profile_pic": "default-profile-pic.gif",
            "files_uploaded": []
        }
    }

    blob = MagicMock()
    blob.download_as_bytes.decode.return_value = json_test_data

    be.content_bucket = MagicMock()
    be.content_bucket.get_blob.return_value = blob

    with patch('json.loads', new_callable=MagicMock) as mock_load:
        mock_load.return_value = json_test_data
        assert be.change_profile_picture("test_user", None, True) == True
        assert json_test_data == expected


def test_get_faq():
    be = Backend()
    blob = MagicMock()
    json_test_data = {
        "FAQ": [{
            "text": "test_question",
            "user": "test_user",
            "replies": []
        }]
    }

    expected = [{"text": "test_question", "user": "test_user", "replies": []}]

    blob.download_as_bytes.decode.return_value = json_test_data
    be.content_bucket = MagicMock()
    be.content_bucket.get_blob.return_value = blob

    with patch('json.loads', new_callable=MagicMock) as mock_load:
        mock_load.return_value = json_test_data
        assert be.get_faq() == expected


def test_submit_question():
    be = Backend()
    blob = MagicMock()

    json_test_data = {
        "FAQ": [{
            "text": "test_question",
            "user": "test_user",
            "replies": []
        }]
    }

    expected = {
        "FAQ": [{
            "text": "test_question",
            "user": "test_user",
            "replies": []
        }, {
            "text": "test_question_2",
            "user": "test_user_2",
            "replies": []
        }]
    }

    be.content_bucket = MagicMock()
    be.content_bucket.get_blob.return_value = blob

    with patch('json.loads', new_callable=MagicMock) as mock_load:
        mock_load.return_value = json_test_data
        be.submit_question("test_user_2", "test_question_2")
        assert json_test_data == expected


def test_submit_reply():
    be = Backend()
    blob = MagicMock()

    json_test_data = {
        "FAQ": [{
            "text": "test_question",
            "user": "test_user",
            "replies": []
        }]
    }

    expected = {
        "FAQ": [{
            "text": "test_question",
            "user": "test_user",
            "replies": [{
                "text": "test_reply",
                "user": "test_user_2"
            }]
        }]
    }

    be.content_bucket = MagicMock()
    be.content_bucket.get_blob.return_value = blob

    with patch('json.loads', new_callable=MagicMock) as mock_load:
        mock_load.return_value = json_test_data
        be.submit_reply("test_user_2", "test_reply", 0)
        assert json_test_data == expected