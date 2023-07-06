import os.path

from django.db import models
from easy_thumbnails.exceptions import InvalidImageFormatError
from easy_thumbnails.fields import ThumbnailerField
from easy_thumbnails.files import Thumbnailer

from .forms import ImageField as ImageFormField


class FileField(ThumbnailerField):
	"""
	File class for compressing all the incoming images.
	"""

	def __init__(self, *args, **kwargs):
		self.resize_source = kwargs.pop("resize_source", (1920, 1080))
		super().__init__(*args, **kwargs)

	def pre_save(self, *args, **kwargs):
		file = super(models.FileField, self).pre_save(*args, **kwargs)
		if file._committed:
			return file

		try:
			thumbnailer = Thumbnailer(file)
			thumbnailer.thumbnail_namer = self.thumbnail_namer  # type: ignore
			thumbnail = thumbnailer.generate_thumbnail({"size": self.resize_source})
		except InvalidImageFormatError:
			return file

		if thumbnail:
			file.name = thumbnail.name
			self.storage.save(thumbnail.name, thumbnail.file, max_length=self.max_length)
		return thumbnail

	@staticmethod
	def thumbnail_namer(source_filename, thumbnail_extension, **kwargs):
		return os.path.splitext(source_filename)[0] + "." + thumbnail_extension

	def formfield(self, **kwargs):
		del kwargs["widget"]
		return super().formfield(**{"form_class": ImageFormField, "max_length": self.max_length, **kwargs})

class ImageField(FileField, models.ImageField):
	"""
	Image class for compressing all the incoming images.
	"""
