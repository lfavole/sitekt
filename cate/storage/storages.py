import os.path
import re

from django.core.exceptions import SuspiciousFileOperation
from django.core.files.storage import FileSystemStorage
from django.utils.crypto import get_random_string
from django.utils.functional import keep_lazy_text
from unidecode import unidecode


@keep_lazy_text
def get_valid_filename(filename: str):
	"""
	Get a valid filename from the given filename.
	"""
	filename = unidecode(filename)

	def normalize(part):
		part = re.sub(r"[^\w.]+|_+", "-", part)
		part = re.sub(r"-{2,}", "-", part)
		part = part.strip("-")
		return part

	name, ext = os.path.splitext(filename)
	name = normalize(name)
	ext = normalize(ext)
	filename = name + ext
	if not filename:
		raise SuspiciousFileOperation(f"Could not derive file name from '{filename}'")
	return filename

class CustomFileSystemStorage(FileSystemStorage):
	"""
	Custom filesystem storage that uses a custom filename generator.
	"""
	def get_valid_name(self, name: str):
		return get_valid_filename(name)

	def get_alternative_name(self, file_root: str, file_ext: str):
		return f"{file_root}.{get_random_string(8, '0123456789abcdef')}{file_ext}"
