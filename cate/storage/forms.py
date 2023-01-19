from django import forms
from easy_thumbnails.widgets import ImageClearableFileInput


class ImageField(forms.ImageField):
	"""
	File field with a thumbnail of the image next to the image file.
	"""
	widget = ImageClearableFileInput
