from django.utils.safestring import mark_safe, SafeData
from easy_thumbnails.widgets import ImageClearableFileInput


class CustomImageClearableFileInput(ImageClearableFileInput):
    """
    Widget that renders the thumbnail in a `<p>` to avoid display glitches.
    """

    def render(self, *args, **kwargs):
        ret = super().render(*args, **kwargs)
        if ret.startswith("<input"):  # no picture selected
            return ret

        is_safe = isinstance(ret, SafeData)

        # remove display:block on label
        ret = ret.replace("<label", '<label style="display:inline"')
        # wrap all this in a paragraph
        ret = f'<p class="file-upload">{ret}</p>'
        if is_safe:
            ret = mark_safe(ret)
        return ret
