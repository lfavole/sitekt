import importlib
from typing import Any, Type

import custom_settings
from common.models import CommonPage
from common.views import CommonPageView
from django.http import HttpRequest
from django.utils.timezone import now


def now_variable(_request: HttpRequest):
    return {"now": now()}

def offline(_request: HttpRequest):
    return {"offline": custom_settings.OFFLINE}

def app_name(request: HttpRequest):
    match = request.resolver_match
    return {"app": match.app_name if match else ""}

def navbar_processor(request):
    match = request.resolver_match
    if match:
        app = match.app_name
    else:
        app = None
    if not app:
        return {"pages": [], "display_navbar": False}
    try:
        PageView: Type[CommonPageView] = importlib.import_module(app + ".views").PageView # pylint: disable=C0103
    except (ImportError, AttributeError):
        return {"pages": [], "display_navbar": False}

    pages_list = PageView(request = request).get_queryset()

    def get_pages(parent):
        pages_query = pages_list.filter(parent_page = parent)
        pages: list[tuple[CommonPage, Any]] = []
        for page in pages_query:
            pages.append((page, get_pages(page)))
        return pages

    return {"pages": get_pages(None), "display_navbar": True}
