import datetime as dt
import os
from django.core.files.storage import Storage
from django.utils.deconstruct import deconstructible
import requests


@deconstructible
class BlobFileStorage(Storage):
    """A storage adapter that connects to a Vercel Blob."""
    # Most of the code was reverse engineered from
    # https://github.com/vercel/storage/tree/main/packages/blob/src/

    def __init__(self, folder="", token=None):
        """
        folder: base folder that will hold the contents of the storage
                (useful if you use multiple storages on the same Blob).
        token: `BLOB_READ_WRITE_TOKEN` given by Vercel. Required.
        """
        self.folder = folder.rstrip("/")
        if self.folder:
            self.folder += "/"
        self._prefix = None
        self._token = token or os.environ.get("BLOB_READ_WRITE_TOKEN")
        if not self._token:
            raise ValueError("A token is required to use BlobFileStorage")

    def _request(self, method, url, *, data=None, json=None, headers=None):
        """Make a request to the Vercel Blob API."""
        headers = {
            "Authorization": f"Bearer {self._token}",
            "X-API-Version": "7",
            **(headers or {}),
        }
        params = None
        # pass data as query string parameters if the method is GET
        if method == "GET":
            params = data
            data = None
        resp = requests.request(
            method,
            f"https://blob.vercel-storage.com/{url}",
            params=params,
            data=data,
            json=json,
            headers=headers,
        )
        try:
            resp.raise_for_status()
        except requests.HTTPError as err:
            # if there is an error, raise a second error with the content of the response
            # (which is more useful than the error code)
            raise requests.HTTPError(resp.text) from err
        return resp.json()

    def delete(self, name):
        """Delete a file."""
        self._request("POST", "delete", json={"urls": [self.folder + name]})

    def exists(self, name):
        """Check if a file exists."""
        try:
            self.get_info(name)
            return True
        except FileNotFoundError:
            return False

    def listdir(self, path):
        data = self._request("GET", "", data={"prefix": self.folder + path.rstrip("/") + "/", "mode": "folded"})
        return data["folders"], [file["pathname"] for file in data["blobs"]]

    def size(self, name):
        data = self._request("GET", "", data={"url": self.url(name)})
        return data["size"]

    def get_info(self, name):
        """Return information about a blob as provided by the Vercel API."""
        name = name or ""

        data = self._request("GET", "", data={"prefix": self.folder + name})
        if not data["blobs"]:
            raise FileNotFoundError(f"The file {name} doesn't exist")

        # save the prefix for later use
        self._prefix = data["blobs"][0]["url"].removesuffix(name).rstrip("/").removesuffix(self.folder).rstrip("/")
        return data["blobs"][0]

    def url(self, name):
        """
        Return a URL for the specified file.

        This function will raise `FileNotFoundError` during the first run if the file doesn't exist.
        """
        if self._prefix:
            return f"{self._prefix}{self.folder}/{name}"

        return self.get_info(name)["url"]

    def save(self, name, content, max_length=None):
        """Save a file to the Vercel Blob."""
        name = self.get_available_name(name, max_length)  # type: ignore
        self._request("PUT", self.folder + name, data=content.read(), headers={"X-Add-Random-Suffix": "false"})
        return name

    def get_created_time(self, name):
        """Return the creation date and time of a file."""
        return dt.datetime.fromisoformat(self.get_info(name)["uploadedAt"])

    # the Vercel Blob API returns only one date, so we use the same method as above
    # for the last access and last change date
    get_accessed_time = get_created_time
    get_modified_time = get_created_time
