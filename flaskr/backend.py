# TODO(Project 1): Implement Backend according to the requirements.
from google.cloud import storage

# Create mock backend in file to test.

class Backend:

    def __init__(self):
        self.password_bucket = "usersandpasswords"
        self.content_bucket = "awesomewikicontent"
        self.storage_client = storage.Client()
        
    def get_wiki_page(self, name):
        bucket = self.storage_client.bucket(self.content_bucket)
        blob = bucket.get_blob(name)
        return blob.download_as_string().decode("utf-8")

    def get_all_page_names(self):
        page_names = []
        blobs = self.storage_client.list_blobs(self.content_bucket)
        for blob in blobs:
            if blob.name.endswith(".html"):
                page_names.append(blob.name)
        return page_names

    def upload(self, name, file):
        bucket = self.storage_client.bucket(self.content_bucket)
        file_type = file.filename.split(".")[-1]
        blob = bucket.blob(f"{name}.{file_type}")
        if blob.exists():
            return False
        else:
            blob.upload_from_file(file)
            return True

    def sign_up(self, username, password):
        bucket = self.storage_client.bucket(self.password_bucket)
        blob = bucket.blob(username)
        if blob.exists():
            return False
        else:
            with blob.open("w") as b:
                b.write(password)
            return True

    def sign_in(self, username, password):
        bucket = self.storage_client.bucket(self.password_bucket)
        blob = bucket.get_blob(username)
        if not blob:
            return False
        else:
            with blob.open("r") as b:
                if b.read() == password:
                    return True
                return False

    # def get_image(self, name):
    #     bucket = self.storage_client.bucket(self.content_bucket)
    #     blob = bucket.get_blob(name)
    #     return blob.download_to_filename(f'{name}.png')

    def get_image(self, names):
        bucket = self.storage_client.bucket(self.content_bucket)
        images = []
        for name in names:
            blob = bucket.get_blob(name)
            image_data = blob.download_as_bytes()
            images.append(image_data)
        return images
