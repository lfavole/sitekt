"""
Default settings.

You will have to create a `custom_settings.py` file with the overrides.
"""

import os
import sys
from getpass import getuser
from pathlib import Path
from types import ModuleType
from typing import Any

from cate.utils.connectivity import internet

PA_SITE = os.environ.get("PYTHONANYWHERE_SITE", "")
PYTHONANYWHERE = bool(PA_SITE)
USERNAME = getuser()

HOST = USERNAME + "." + PA_SITE if PYTHONANYWHERE else "*"
DEBUG = False
SECRET_KEY = ""

USE_SQLITE = not PYTHONANYWHERE
REAL_DB_NAME = "cate"

GITHUB_REPO = "https://github.com/lfavole/sitekt"
GITHUB_WEBHOOK_KEY = None


class CustomSettings(ModuleType):
    """
    Class for shadowing this module.
    It provides access to attributes that depend on other attributes for ease of use.
    """

    def __getattribute__(self, name) -> Any:
        if name[:2] == "__" and name[-2:] == "__":
            # short-circuit cf. https://github.com/django/django/blob/f6ed2c3/django/utils/autoreload.py#L118 and l.133
            return super().__getattribute__(name)

        if name == "OFFLINE":
            # return the current value of OFFLINE
            if PYTHONANYWHERE:
                return False
            return not internet()

        try:
            import custom_settings_overrides as cs_overrides

            if getattr(cs_overrides, "TEST", False):
                import custom_settings_test as cs_test

                return getattr(cs_test, name)

            return getattr(cs_overrides, name)
        except AttributeError:
            pass

        if name == "DB_NAME":
            return USERNAME + "$" + self.REAL_DB_NAME

        if PYTHONANYWHERE:
            if name == "HOST":
                return USERNAME + "." + PA_SITE

            if name == "DB_HOST":
                return USERNAME + ".mysql." + PA_SITE.replace("pythonanywhere.com", "pythonanywhere-services.com")

            if name == "DB_USER":
                try:
                    return super().__getattribute__(name)
                except AttributeError:
                    return USERNAME

            if name == "PA_SITE":
                return PA_SITE if PYTHONANYWHERE else None

            if name == "WSGI_FILE":
                return (
                    None
                    if not self.HOST
                    else Path("/var/www") / (self.HOST.replace(".", "_").lower().strip() + "_wsgi.py")
                )

        return super().__getattribute__(name)


sys.modules[__name__].__class__ = CustomSettings  # type: ignore
