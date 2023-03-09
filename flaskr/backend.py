# TODO(Project 1): Implement Backend according to the requirements.
from google.cloud import storage

# Create mock backend in file to test.

class Backend:
    """Retrieves and modifies data from GCS using two buckets, one for passwords and another for content.

    This class will take care of storing and retreving data from the GCS.
    It will store the password bucket name and content bucket name so it can access the buckets and store and retrieve the data received.
    This will upload files and retrieve the file paths for the location of the files indicated.

    Atrributes:
        password_bucket: the name of the bucket where the username is stored inside of a blob and the content is the hashed password.
        content_bucket: the name of the bucket where the uploaded files are stored.
        storage_client: creates the connection with GCS.
    """
    def __init__(self):
        """Initializes the GCS and sets the password and content bucket."""
        self.password_bucket = "usersandpasswords"
        self.content_bucket = "awesomewikicontent"
        self.storage_client = storage.Client()
        
    def get_wiki_page(self, name):
        """Using the name passed as argument, it will retrieve the data from GCS that corresponds to that file.

        Returns:
            A string with all the content of the wiki page requested.
        """
        bucket = self.storage_client.bucket(self.content_bucket)
        blob = bucket.get_blob(name)
        return blob.download_as_string().decode("utf-8")

    def get_all_page_names(self):
        """Retrieves all the uploaded pages from GCS.

        Returns:
            A list with all the page names that end with .html.
        """
        page_names = []
        blobs = self.storage_client.list_blobs(self.content_bucket)
        for blob in blobs:
            if blob.name.endswith(".html"):
                page_names.append(blob.name)
        return page_names

    def upload(self, name, file):
        """Using the file and name given, it will try to create a blob using the file name and store the file inside of the blob

        Returns:
            True if the file was successfully uploaded to GCS.
            False if the file name exists.
        """
        bucket = self.storage_client.bucket(self.content_bucket)
        file_type = file.filename.split(".")[-1]
        blob = bucket.blob(f"{name}.{file_type}")
        if blob.exists():
            return False
        else:
            blob.upload_from_file(file)
            return True

    def sign_up(self, username, password):
        """It will create a new blob inside of the password bucket that has the user name as the blob name and the content will be the hashed password.

        Returns:
            True if it was able to sign up correctly.
            False if the username already exists.
        """
        bucket = self.storage_client.bucket(self.password_bucket)
        blob = bucket.blob(username)
        if blob.exists():
            return False
        else:
            with blob.open("w") as b:
                b.write(password)
            return True

    def sign_in(self, username, password):
        """Retrieves the data given as username and password from the GCS and see if the password matches with the username.

        Returns:
            True if the username exists or if the password matches with the username.
            False if there is no matching username stored or the password doesn't match.
        """
        bucket = self.storage_client.bucket(self.password_bucket)
        blob = bucket.get_blob(username)
        if not blob:
            return False
        else:
            with blob.open("r") as b:
                if b.read() == password:
                    return True
                return False

    def get_image(self, name):
        """Retrieves the image from the content bucket inside of GCS and stores returns the part of the url of where it is stored.

        Returns:
            A string the has part of the path to the GCS location of the image without the base url.
        """
        bucket = self.storage_client.bucket(self.content_bucket)
        blob = bucket.get_blob(name)
        image = f"{self.content_bucket}/{blob.name}"
        return image
