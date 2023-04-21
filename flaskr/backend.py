from google.cloud import storage
import json
import random


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
        """Retrieves the profile picture from the JSON file.

        Args:
            username: the name of the user.

        Returns:
            A string the has part of the path to the GCS location of the profile picture without the base url.
        """
        json_blob = self.content_bucket.get_blob("info.json")
        json_str = json_blob.download_as_bytes().decode()
        json_dict = json.loads(json_str)
        return json_dict[username]["profile_pic"]

    def change_profile_picture(self, username, new_pfp, remove):
        """Changes the user's profile picture.

        Retrieves the user's current profile picture from the JSON file. If remove is True, then the profile picture will be updated to the default. If remove is False, the new profile picture will replace the old one.

        Args:
            username: the name of the user.
            new_pfp: the image file for the new profile picture.
            remove: boolean indicating if user only requested to remove current profile picture.

        Returns:
            True if profile picture was successfully updated.
            False if image was not accepted file type.
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
        """Changes the user's password in the GCS bucket.

        Args:
            username: the name of the user.
            current_password: the current password enterred by the user.
            new_password: the new desired password.

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
        """Changes the current user's username to the new one.

        This modifies the current blob in the password bucket for the user and replaces it with the new username and deletes the old one.
        Also modifies the JSON file for the user so all of their data is transferred to the new username.

        Args:
            current_username: current username of the user.
            new_username: the username the user wants to change to.

        Returns:
            False if the new username the user wants is already taken.
            True if the user is not taken and the username is changed.
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
        """Retrieves the names of all the files the user has uploaded from info.json that stores all the user data.

        Args:
            username: the username of the user that is going to retrieve the uploaded files for.

        Returns:
            A list of the uploaded files from the specified user.
        """
        json_blob = self.content_bucket.get_blob("info.json")
        json_str = json_blob.download_as_bytes().decode()
        json_dict = json.loads(json_str)
        return json_dict[username]["files_uploaded"]

    def delete_uploaded_file(self, username, file_name):
        """Deletes the uploaded file from the user and deletes it in GCS and the user info.json file.

        Args:
            username: the user that needs to remove a file.
            file_name: the uploaded file from the user.

        Returns:
            True once the uploaded file from the user has been deleted.
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
        """Retrieves all the contributors of the wiki from the info.json that is stored in GCS.

        Args:
            username: the user that needs to remove a file.
            file_name: the uploaded file from the user.

        Returns:
            True once the uploaded file from the user has been deleted.
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
        """Adds a new FAQ question to the JSON file.

        Args:
            username: the name of the user.
            question: string containing the question submitted by the user.
        """
        json_blob = self.content_bucket.get_blob("website_info.json")
        json_str = json_blob.download_as_bytes().decode()
        json_dict = json.loads(json_str)
        new_question = {"text": question, "user": username, "replies": []}
        json_dict["FAQ"].append(new_question)
        mod_json_data = json.dumps(json_dict)
        json_blob.upload_from_string(mod_json_data,
                                     content_type="application/json")

    def submit_reply(self, username, reply, question_index):
        """Adds a new FAQ reply to corresponding question in the JSON file.

        Args:
            username: the name of the user.
            reply: string containing the reply submitted by the user.
            question_index = integer representing the question for which the reply is being submitted.
        """
        json_blob = self.content_bucket.get_blob("website_info.json")
        json_str = json_blob.download_as_bytes().decode()
        json_dict = json.loads(json_str)
        new_reply = {"text": reply, "user": username}
        json_dict["FAQ"][int(question_index) - 1]["replies"].append(new_reply)
        mod_json_data = json.dumps(json_dict)
        json_blob.upload_from_string(mod_json_data,
                                     content_type="application/json")

    def get_faq(self):
        """Retrieves all FAQ questions and replies from GCS.

        Returns:
            A list containing all the questions and replies.
        """
        json_blob = self.content_bucket.get_blob("website_info.json")
        json_str = json_blob.download_as_bytes().decode()
        json_dict = json.loads(json_str)
        return json_dict["FAQ"]