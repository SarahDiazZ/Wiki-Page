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

    def upload(self, username, name, file):
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
            json_blob = self.content_bucket.get_blob("info.json")
            json_str = json_blob.download_as_bytes().decode()
            json_dict = json.loads(json_str)
            json_dict[username]["files_uploaded"].append(f"{name}.{file_type}")
            blob.upload_from_file(file)
            mod_json_data = json.dumps(json_dict)
            json_blob.upload_from_string(mod_json_data,
                                         content_type="application/json")
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
            blob.upload_from_string(password,
                                    content_type="application/octet-stream")
            json_blob = self.content_bucket.get_blob("info.json")
            json_str = json_blob.download_as_bytes().decode()
            json_dict = json.loads(json_str)
            profile = "default-profile-pic.gif"
            if random.randint(1, 20) == 2:
                profile = "default-profile-pic2.gif"
            json_dict[username] = {"profile_pic": profile, "files_uploaded": []}
            json_data = json.dumps(json_dict)
            json_blob.upload_from_string(json_data,
                                         content_type="application/json")
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
        '''
        '''
        json_blob = self.content_bucket.get_blob("info.json")
        json_str = json_blob.download_as_bytes().decode()
        json_dict = json.loads(json_str)
        return json_dict[username]["profile_pic"]

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

            if file_type not in [
                    "png", "PNG", "jpeg", "JPG", "jpg", "JPEG", "gif", "GIF"
            ]:
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
        """Summary.

        Args:
            username:
            current_username:
            new_username:

        Returns:
            True if.
            False if.
        """
        new_blob = self.password_bucket.blob(new_username)
        if new_blob.exists():
            return False
        json_blob = self.content_bucket.get_blob("info.json")
        json_str = json_blob.download_as_bytes().decode()
        json_dict = json.loads(json_str)
        user_info = json_dict.pop(current_username)
        json_dict[new_username] = user_info
        mod_json_data = json.dumps(json_dict)
        json_blob.upload_from_string(mod_json_data,
                                     content_type="application/json")
        old_blob = self.password_bucket.get_blob(current_username)
        self.password_bucket.copy_blob(old_blob,
                                       self.password_bucket,
                                       new_name=new_username)
        old_blob.delete()
        return True

    def get_user_files(self, username):
        """Summary.

        Args:
            username:

        Returns:
            Something
        """
        json_blob = self.content_bucket.get_blob("info.json")
        json_str = json_blob.download_as_bytes().decode()
        json_dict = json.loads(json_str)
        return json_dict[username]["files_uploaded"]

    def delete_uploaded_file(self, username, file_name):
        """Summary.

        Args:
            username:
            file_name:

        Returns:
            Nothing.
        """
        blob = self.content_bucket.get_blob(file_name)
        blob.delete()
        json_blob = self.content_bucket.get_blob("info.json")
        json_str = json_blob.download_as_bytes().decode()
        json_dict = json.loads(json_str)
        json_dict[username]["files_uploaded"].remove(file_name)
        mod_json_data = json.dumps(json_dict)
        json_blob.upload_from_string(mod_json_data,
                                     content_type="application/json")
        return json_dict[username]["files_uploaded"]

    def get_contributors(self):
        """
        """
        json_blob = self.content_bucket.get_blob("info.json")
        json_str = json_blob.download_as_bytes().decode()
        json_dict = json.loads(json_str)
        contributors = []
        for contributor in json_dict.keys():
            if len(json_dict[contributor]["files_uploaded"]) > 0:
                contributors.append(contributor)
        return contributors

    def submit_question(self, username, question):
        '''
        '''
        json_blob = self.content_bucket.get_blob("website_info.json")
        json_str = json_blob.download_as_bytes().decode()
        json_dict = json.loads(json_str)
        new_question = {"text": question, "user": username, "replies": []}
        json_dict["FAQ"].append(new_question)
        mod_json_data = json.dumps(json_dict)
        json_blob.upload_from_string(mod_json_data,
                                     content_type="application/json")

    def submit_reply(self, username, reply, question_index):
        '''
        '''
        json_blob = self.content_bucket.get_blob("website_info.json")
        json_str = json_blob.download_as_bytes().decode()
        json_dict = json.loads(json_str)
        new_reply = {"text": reply, "user": username}
        json_dict["FAQ"][int(question_index) - 1]["replies"].append(new_reply)
        mod_json_data = json.dumps(json_dict)
        json_blob.upload_from_string(mod_json_data,
                                     content_type="application/json")

    def get_faq(self):
        '''
        '''
        json_blob = self.content_bucket.get_blob("website_info.json")
        json_str = json_blob.download_as_bytes().decode()
        json_dict = json.loads(json_str)
        return json_dict["FAQ"]