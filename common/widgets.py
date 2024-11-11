from easy_thumbnails.widgets import ImageClearableFileInput


class CustomImageClearableFileInput(ImageClearableFileInput):
    """
    Widget that renders the thumbnail in a `<p>` to avoid display glitches.
    """

    def render(self, *args, **kwargs):
        ret = super().render(*args, **kwargs)
        if ret.startswith("<input"):  # no picture selected
            return ret

        # remove display:block on label
        ret = ret.replace("<label", '<label style="display:inline"')
        # wrap all this in a paragraph
        return f'<p class="file-upload">{ret}</p>'
