import os
from django.conf import settings
from django.http import HttpRequest
from django.utils.timezone import now

from common.models import Page
from common.models import SiteMessage
from django.contrib.messages import constants as message_constants
from django.contrib.messages import add_message


def now_variable(_request: HttpRequest):
    return {"now": now()}


def offline(_request: HttpRequest):
    return {"offline": bool(os.environ.get("OFFLINE"))}


def app_name(request: HttpRequest):
    match = request.resolver_match
    return {"app": match.app_name if match else ""}


def site_name(_request: HttpRequest):
    return {"SITE_NAME": settings.SITE_NAME}


def homepage(_request: HttpRequest):
    return {"HOME_TEMPLATE": Page.HOME_TEMPLATE}


def site_message(request: HttpRequest):
    """If an active SiteMessage exists, add it to Django messages for public pages.

    Excludes admin and account pages.
    """
    path = request.path or ""
    if path.startswith("/admin") or path.startswith("/accounts") or path.startswith("/accounts/"):
        return {}

    try:
        msg = SiteMessage.objects.filter(is_active=True).order_by("-created_at").first()
    except Exception:
        return {}

    if not msg:
        return {}

    level_map = {
        "DEBUG": message_constants.DEBUG,
        "INFO": message_constants.INFO,
        "SUCCESS": message_constants.SUCCESS,
        "WARNING": message_constants.WARNING,
        "ERROR": message_constants.ERROR,
    }
    level = level_map.get(msg.level, message_constants.INFO)

    add_message(request, level, msg.message)
    return {}
