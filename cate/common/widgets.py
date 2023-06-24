from easy_thumbnails.widgets import ImageClearableFileInput


class CustomImageClearableFileInput(ImageClearableFileInput):
    """
    Widget that renders the thumbnail in a `<p>` to avoid display glitches.
    """
    def render(self, *args, **kwargs):
        ret = super().render(*args, **kwargs)
        if ret.startswith("<input"):
            return ret
        return f'<p class="file-upload">{ret}</p>'
