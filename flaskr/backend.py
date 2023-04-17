from google.cloud import storage
import json
import random

# Create mock backend in file to test.


class Backend:
    """Retrieves and modifies data from GCS using two buckets, one for passwords and another for content.

    This class will take care of storing and retreving data from the GCS.
    It will store the password bucket name and content bucket name so it can access the buckets and store and retrieve the data received.
    This will upload files and retrieve the file paths for the location of the files indicated.

    Atrributes:
        password_b: the name of the bucket where the username is stored inside of a blob and the content is the hashed password.
        content_b: the name of the bucket where the uploaded files are stored.
        storage_client: creates the connection with GCS.
        content_bucket: connection to the content bucket on GCS.
        password_bucket: connection to the password bucket on GCS.
    """

    def __init__(self):
        """Initializes the GCS and sets the password and content bucket."""
        self.storage_client = storage.Client()
        self.password_b = "usersandpasswords"
        self.content_b = "awesomewikicontent"
        self.password_bucket = self.storage_client.bucket(self.password_b)
        self.content_bucket = self.storage_client.bucket(self.content_b)

    def get_wiki_page(self, name):
        """Using the name passed as argument, it will retrieve the data from GCS that corresponds to that file.

        Args:
            name: the name of the wiki page that is being looked up on the GCS content bucket.

        Returns:
            A string with all the content of the wiki page requested.
        """
        blob = self.content_bucket.get_blob(name)
        return blob.download_as_bytes().decode()

    def get_all_page_names(self):
        """Retrieves all the uploaded pages from GCS.

        Returns:
            A list with all the page names that end with .html.
        """
        page_names = []
        blobs = self.content_bucket.list_blobs()
        for blob in blobs:
            if blob.name.endswith(".html"):
                page_names.append(blob.name)
        return page_names

    def upload(self, name, file):
        """Using the file and name given, it will try to create a blob using the file name and store the file inside of the blob

        Args:
            name: the naming of the file that will be stored on the GCS content bucket.
            file: the file that will be stored on the GCS content bucket.

        Returns:
            True if the file was successfully uploaded to GCS.
            False if the file name exists.
        """
        file_type = file.filename.split(".")[-1]
        blob = self.content_bucket.blob(f"{name}.{file_type}")
        if blob.exists():
            return False
        else:
            blob.upload_from_file(file)
            return True

    def sign_up(self, username, password):
        """It will create a new blob inside of the password bucket that has the user name as the blob name and the content will be the hashed password.

        Args:
            username: the username that will be stored as the GCS password bucket blob.
            password: the hashed password that gets stored inside of the created blob.

        Returns:
            True if it was able to sign up correctly.
            False if the username already exists.
        """
        blob = self.password_bucket.blob(username)
        if blob.exists():
            return False
        else:
            blob.upload_from_string(password)
            return True

    def sign_in(self, username, password):
        """Retrieves the data given as username and password from the GCS and see if the password matches with the username.

        Args:
            username: the username that will be checked as the GCS password bucket blob.
            password: the hashed password that matches what is inside the indicated blob.

        Returns:
            True if the username exists or if the password matches with the username.
            False if there is no matching username stored or the password doesn't match.
        """
        blob = self.password_bucket.get_blob(username)
        if not blob:
            return False
        else:
            if blob.download_as_bytes().decode() == password:
                return True
            return False

    def get_image(self, name):
        """Retrieves the image from the content bucket inside of GCS and stores returns the part of the url of where it is stored.

        Args:
            name: the name of the image that needs to be retrieved.

        Returns:
            A string the has part of the path to the GCS location of the image without the base url.
        """
        blob = self.content_bucket.get_blob(name)
        image = f"{self.content_b}/{blob.name}"
        return image

    def get_profile_pic(self, username):
        #TODO
        return "default-profile-pic.gif"

    def change_profile_picture(self, username, new_pfp, remove):
        """Summary.

        Args:
            username: 
            new_pfp:
            remove:

        Returns:
            True if
            False if
        """
        json_blob = self.content_bucket.get_blob("info.json")
        json_str = json_blob.download_as_bytes().decode()
        json_dict = json.loads(json_str)
        old_pfp = json_dict[username]["profile_pic"]
        old_blob = self.content_bucket.get_blob(old_pfp)

        if remove:
            old_blob.delete()
            json_dict[username]["profile_pic"] = "default-profile-pic.gif"

        else:
            file_type = new_pfp.filename.split(".")[-1]

            if file_type not in ["png", "jpeg", "jpg", "gif"]:
                return False

            if old_pfp != "default-profile-pic.gif" and old_pfp != "default-profile-pic2.gif":
                old_blob.delete()

            file_name = f"{username}-profile-picture-superduperteamawesome.{file_type}"
            blob = self.content_bucket.blob(file_name)
            blob.upload_from_file(new_pfp)
            json_dict[username]["profile_pic"] = file_name

        mod_json_data = json.dumps(json_dict)
        json_blob.upload_from_string(mod_json_data,
                                     content_type="application/json")
        return True

    def change_password(self, username, current_password, new_password):
        """Summary.

        Args:
            username: 
            current_password:
            new_password:

        Returns:
            True if the current password is correct and password is updated.
            False if current password is incorrect and password was not updated.
        """
        blob = self.password_bucket.get_blob(username)

        if blob.download_as_string().decode() == current_password:
            blob.upload_from_string(new_password)
            return True

        return False

    def change_username(self, current_username, new_username):
        #TODO
        return True

    def get_user_files(self, username):
        #TODO
        return ["test1.png", "test2.jpg", "test3.html"]

    def delete_uploaded_file(self, username, file_name):
        #TODO
        pass

    def get_contributors(self):
        """
        """
        json_blob = self.content_bucket.get_blob("info.json")
        json_str = json_blob.download_as_bytes().decode()
        json_dict = json.loads(json_str)
        contributors = []
        for contributor in json_dict.keys():
            contributors.append(contributor)
        return contributors
