from typing import Type

from django.core.paginator import Paginator
from django.db.models import Model
from django.db.models.query import QuerySet
from django.http import HttpRequest


def paginate(request: HttpRequest, queryset: Type[Model] | QuerySet, number=100):
    """
    Paginate a queryset with a specified number of elements on each page.
    This uses the `page` GET parameter.

    Usage:
    >>> from django.shortcuts import render
    >>> def view(request):
    ...     return render(request, "template.html", {
    ...         "page_obj": paginate(request, Model),
    ...     })

    In the template: `{% include "cate/paginator.html" %}`.
    The variable must be named `page_obj`.
    """
    if isinstance(queryset, type) and issubclass(queryset, Model):
        queryset = queryset.objects.all()  # type: ignore
    paginator = Paginator(queryset, number)
    page_number = request.GET.get("page")
    return paginator.get_page(page_number)
