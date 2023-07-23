from cate.utils.paginator import paginate
from common.views import has_permission
from django.contrib import messages
from django.core.exceptions import PermissionDenied
from django.http import HttpRequest, HttpResponse
from django.shortcuts import get_object_or_404, redirect, render
from django.utils.translation import gettext_lazy as _

from .forms import ErrorForm
from .models import Error


def check_permission(f):
    def wrapper(request, *args, **kwargs):
        if not has_permission(request, Error):
            raise PermissionDenied
        return f(request, *args, **kwargs)

    return wrapper


@check_permission
def display_error(_request, pk: int):
    """
    Display an error.
    """
    error = get_object_or_404(Error, pk=pk)
    return HttpResponse(error.content)


@check_permission
def errors_list(request: HttpRequest):
    """
    Show the list of all errors.
    """
    id_str: str | None = request.GET.get("id")
    if id_str is not None:
        try:
            id = int(id_str)
        except ValueError:
            messages.add_message(request, messages.WARNING, _("'%s' is not a valid error ID.") % id_str)
            return redirect("errors:errors_list")

        if Error.objects.filter(pk=id).exists():
            messages.add_message(request, messages.WARNING, _("The error with ID %d doesn't exist.") % id)
            return redirect("errors:error", id)
        return redirect("errors:errors_list")

    return render(
        request,
        "errors/errors_list.html",
        {
            "form": ErrorForm(),
            "page_obj": paginate(request, Error),
        },
    )
