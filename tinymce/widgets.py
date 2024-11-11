# Copyright (c) 2008 Joost Cassee
# Licensed under the terms of the MIT License (see LICENSE.txt)

"""
This TinyMCE widget was copied and extended from this code by John D'Agostino:
http://code.djangoproject.com/wiki/CustomWidgetsTinyMCE
"""
import json

from django import forms
from django.contrib.admin import widgets as admin_widgets
from django.core.serializers.json import DjangoJSONEncoder
from django.forms.utils import flatatt
from django.utils.html import escape
from django.utils.safestring import mark_safe
from django.utils.translation import get_language, to_locale

from . import settings as tinymce_settings


def get_language_from_django():
    language = get_language()
    language = to_locale(language) if language is not None else "en_US"
    return language


class TinyMCE(forms.Textarea):
    """
    TinyMCE widget. Set settings.TINYMCE_JS_URL to set the location of the
    javascript file. Default is "STATIC_URL + 'tinymce/tinymce.min.js'".
    You can customize the configuration with the mce_attrs argument to the
    constructor.

    In addition to the standard configuration you can set the
    'content_language' parameter. It takes the value of the 'language'
    parameter by default.

    In addition to the default settings from settings.TINYMCE_DEFAULT_CONFIG,
    this widget sets the 'language', 'directionality' and
    'spellchecker_languages' parameters by default. The first is derived from
    the current Django language, the others from the 'content_language'
    parameter.
    """

    def __init__(self, content_language=None, attrs=None, mce_attrs=None):
        super().__init__(attrs)
        self.mce_attrs = mce_attrs or {}
        self.content_language = content_language

    def use_required_attribute(self, *args):
        # The html required attribute may disturb client-side browser validation.
        return False

    def get_mce_config(self, attrs):
        mce_config = tinymce_settings.DEFAULT_CONFIG.copy()
        if "language" not in mce_config:
            mce_config["language"] = get_language_from_django()
        if mce_config["language"] == "en_US":
            del mce_config["language"]
        else:
            # https://www.tiny.cloud/docs/tinymce/6/ui-localization/#supported-languages
            languages = {
                lang[:2]: lang
                for lang in (
                    "ar eu bg_BG ca zh_CN zh_TW hr cs da nl fi fr_FR de el he_IL hi hu_HU id it ja kk ko_KR ms nb_NO "
                    "fa pl pt_BR pt_PT ro ru sk sl_SI es sv_SE th_TH tr uk vi"
                ).split()
            }
            mce_config["language"] = languages[mce_config["language"][:2]]
        mce_config.update(self.mce_attrs)
        # Assuming that if selector is present, it should include "textarea".
        if not mce_config.get("selector"):
            mce_config["selector"] = f"#{attrs['id']}"
        return mce_config

    def render(self, name, value, attrs=None, renderer=None):
        if value is None:
            value = ""
        final_attrs = self.build_attrs(self.attrs, attrs)
        final_attrs["name"] = name
        if final_attrs.get("class", None) is None:
            final_attrs["class"] = ""
        final_attrs["class"] += " tinymce"  # type: ignore
        assert "id" in final_attrs, "TinyMCE widget attributes must contain 'id'"

        mce_config = self.get_mce_config(final_attrs)
        mce_config["content_css"] = list(mce_config["content_css"])
        final_attrs["data-mce-conf"] = json.dumps(mce_config, cls=DjangoJSONEncoder)
        return mark_safe(f"<textarea{flatatt(final_attrs)}>{escape(value)}</textarea>")

    @property
    def media(self):
        css = None
        js = [str(tinymce_settings.JS_URL)]  # might be a proxy
        if tinymce_settings.USE_EXTRA_MEDIA:
            if "js" in tinymce_settings.USE_EXTRA_MEDIA:
                js += tinymce_settings.USE_EXTRA_MEDIA["js"]

            if "css" in tinymce_settings.USE_EXTRA_MEDIA:
                css = tinymce_settings.USE_EXTRA_MEDIA["css"]
        js.append("django_tinymce/init_tinymce.js")
        return forms.Media(css=css, js=js)


class AdminTinyMCE(TinyMCE, admin_widgets.AdminTextareaWidget):
    pass
