import os.path
import re

from django.core.exceptions import SuspiciousFileOperation
from django.core.files.storage import FileSystemStorage
from django.utils.functional import keep_lazy_text
from unidecode import unidecode


@keep_lazy_text
def get_valid_filename(filename: str):
	"""
	Get a valid filename from the given filename.
	"""
	filename = unidecode(str(filename)) # type: ignore

	def normalize(part):
		part = part.replace("_", "-") # because \w includes _
		part = re.sub(r"[^\w.]", "-", part)
		return re.sub(r"-{2,}", "-", part).strip("-")

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

	def __init__(self, *args, **kwargs):
		super().__init__(*args, **kwargs)
		self.counter_cache: tuple[str, int] = ("", 0)

	def generate_filename(self, filename: str):
		return get_valid_filename(filename)

	def get_alternative_name(self, file_root: str, file_ext: str):
		file = file_root + file_ext
		# keep only the last needed file; other files may have changed
		if file is not self.counter_cache[0]:
			counter = -1
		else:
			counter = self.counter_cache[1]
		counter += 1
		self.counter_cache = (file, counter)
		return f"{file_root}{'-' + str(counter) if counter else ''}{file_ext}"
