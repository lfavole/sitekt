import importlib
from typing import Any, Type

from django.http import HttpRequest
from django.utils.timezone import now
from common.models import CommonPage
from common.views import CommonPageView


def app_name(request: HttpRequest):
    return {"app": request.resolver_match.app_name}

def now_variable(_request: HttpRequest):
    return {"now": now()}

def navbar_processor(request):
    app = app_name(request)["app"]
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
