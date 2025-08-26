import os.path
from urllib.parse import urlencode

from common.widgets import CustomImageClearableFileInput
from django.core.files.base import ContentFile
from django.db import models
from easy_thumbnails.engine import NoSourceGenerator
from easy_thumbnails.exceptions import InvalidImageFormatError
from easy_thumbnails.fields import ThumbnailerField
from easy_thumbnails.files import Thumbnailer, ThumbnailFile


class FileField(ThumbnailerField):
    """
    File field class for compressing all the incoming images.
    """

    def __init__(self, *args, **kwargs):
        self.resize_source = kwargs.pop("resize_source", (1920, 1080))
        super().__init__(*args, **kwargs)

    def pre_save(self, *args, **kwargs):
        file = super(models.FileField, self).pre_save(*args, **kwargs)
        if file._committed:
            # Don't bother compressing the file if it's already saved
            return file

        thumbnailer = Thumbnailer(file)
        thumbnailer.thumbnail_namer = self.thumbnail_namer  # type: ignore
        thumbnailer.thumbnail_basedir = str(self.storage.base_location)  # type: ignore
        thumbnailer.thumbnail_subdir = ""  # type: ignore
        thumbnailer.thumbnail_prefix = ""  # type: ignore
        try:
            thumbnail = thumbnailer.old_generate_thumbnail({"size": self.resize_source, "autocrop": True})
        except (InvalidImageFormatError, NoSourceGenerator):
            pass
        else:
            file.name = os.path.join(os.path.dirname(file.name), os.path.basename(thumbnail.name))
            file.file = thumbnail.file

        if file and not file._committed:
            file.save(file.name, file.file, save=False)

        return file

    @staticmethod
    def thumbnail_namer(source_filename, thumbnail_extension, **kwargs):
        return os.path.splitext(source_filename)[0] + "." + thumbnail_extension


class ImageField(FileField, models.ImageField):
    """
    Image class for compressing all the incoming images.
    """

    def formfield(self, **kwargs):
        del kwargs["widget"]
        return super().formfield(**{"widget": CustomImageClearableFileInput, "max_length": self.max_length, **kwargs})


# Generate thumbnails using Next.js on Vercel
if os.environ.get("VERCEL"):
    old_generate_thumbnail = Thumbnailer.generate_thumbnail

    class CustomThumbnailFile(ThumbnailFile):
        def __init__(self, source_url, thumbnail_options):
            base_url = os.environ.get("VERCEL_URL", "")
            if base_url:
                base_url = f"https://{base_url}"
            url = f"{base_url}/_vercel/image?" + urlencode({
                "url": source_url,
                "w": thumbnail_options["size"][0],
                "q": 85,
            })
            super().__init__(url)

        @property
        def url(self):
            return self.name

    def generate_thumbnail(self, thumbnail_options, *args, **kwargs):
        if thumbnail_options.get("crop"):
            return old_generate_thumbnail(self, thumbnail_options)
        return CustomThumbnailFile(self.source_storage.url(self.name), thumbnail_options, *args, **kwargs)

    Thumbnailer.generate_thumbnail = generate_thumbnail
    Thumbnailer.old_generate_thumbnail = old_generate_thumbnail

    old_save_thumbnail = Thumbnailer.save_thumbnail

    def save_thumbnail(self, thumbnail, *args, **kwargs):
        # Don't save custom thumbnails
        if isinstance(thumbnail, CustomThumbnailFile):
            return
        return old_save_thumbnail(self, thumbnail, *args, **kwargs)

    Thumbnailer.save_thumbnail = save_thumbnail
else:
    Thumbnailer.old_generate_thumbnail = Thumbnailer.generate_thumbnail
