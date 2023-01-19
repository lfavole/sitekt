import os.path
from io import BytesIO

from django.core.files.base import File
from django.db import models
from easy_thumbnails.fields import ThumbnailerImageField
from PIL import Image

from .forms import ImageField as ImageFormField


class ImageField(ThumbnailerImageField):
	"""
	Image class for compressing all the incoming images.
	"""

	def pre_save(self, *args, **kwargs):
		file = super(models.FileField, self).pre_save(*args, **kwargs)
		if file._committed:
			return file

		img = Image.open(file)
		max_size = (1920, 1080)

		if img.width > max_size[0] or img.height > max_size[1]:
			file.name = os.path.splitext(file.name)[0] + ".jpg"
			img.thumbnail(max_size)
			output_stream = BytesIO()
			output_stream.name = file.name
			img.save(output_stream)
			file.save(file.name, output_stream, save = False)
			output_stream.name = file.name
			return File(output_stream)

		del img
		if file and not file._committed:
			file.save(file.name, file.file, save = False)
		return file

	def formfield(self, **kwargs):
		del kwargs["widget"]
		return super().formfield(**{"form_class": ImageFormField, "max_length": self.max_length, **kwargs})
