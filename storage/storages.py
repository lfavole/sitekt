# These are the real storage adapters used by the website.
from django.core.files.storage import FileSystemStorage

from .blob import BlobFileStorage
from .filename_hash import FilenameHashMixin


class CustomFileSystemStorage(FilenameHashMixin, FileSystemStorage):
    """
    Custom filesystem storage that adds a random hash to every created filename.
    """


class CustomBlobStorage(FilenameHashMixin, BlobFileStorage):
    """
    Custom Vercel Blob storage that adds a random hash to every created filename.
    """
