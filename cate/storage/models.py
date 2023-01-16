import os.path

from django.core.files.base import ContentFile
from filer.models.abstract import BaseImage as FilerImage
from PIL import Image as PillowImage


class Image(FilerImage):
	"""
	Image class for compressing all the incoming images.
	"""

	def save(self, *args, **kwargs):
		super().save(*args, **kwargs)
		path = self.file_ptr.path
		img = PillowImage.open(path)
		print(f"{img=}")
		print(f"{img.size=}")
		max_size = (1920, 1080)
		if img.width > max_size[0] or img.height > max_size[1]:
			print(f"{img=}")
			new_path = os.path.splitext(path)[0] + ".png"
			img.thumbnail(max_size)
			img.save(new_path)

			src_path = self.file.name # type: ignore
			dest_path = new_path

			if self.is_public:
				storage = self.file.storages['public'] # type: ignore
			else:
				storage = self.file.storages['private'] # type: ignore

			src_file = storage.open(src_path)
			with src_file.open() as f:
				content_file = ContentFile(f.read())
			self.file = storage.save(dest_path, content_file)
			storage.delete(src_path)

			# self.file_ptr.path = new_path
			# super().save()
			# self.file_data_changed()
		else:
			del img
		# super().save(*args, **kwargs)

	class Meta(FilerImage.Meta):
		abstract = False
		app_label = "storage"
