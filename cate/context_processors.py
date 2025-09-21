import os
from django.conf import settings
from django.http import HttpRequest
from django.utils.timezone import now

from common.models import Page


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
