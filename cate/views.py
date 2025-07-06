import datetime as dt
import hmac
import importlib
import mimetypes
import os
import sys
from hashlib import sha1
from ipaddress import ip_address, ip_network
from itertools import chain
from pathlib import Path
from typing import Type
from urllib.parse import quote, urlparse

import requests
from common.models import ImageBase
from common.views import _encode_filename, has_permission
from django.apps import apps
from django.conf import settings
from django.contrib.contenttypes.models import ContentType
from django.core.serializers import deserialize, get_serializer, _serializers
from django.http import (
    FileResponse,
    Http404,
    HttpRequest,
    HttpResponse,
    HttpResponseForbidden,
    HttpResponseNotAllowed,
    HttpResponseServerError,
    JsonResponse,
)
from django.shortcuts import get_object_or_404, render, resolve_url
from django.template import Context, Engine, RequestContext
from django.template import context_processors as django_cps
from django.utils.encoding import force_bytes
from django.utils.safestring import SafeString
from django.utils.translation import gettext_lazy as _
from django.views.debug import ExceptionReporter, technical_404_response
from django.views.decorators.csrf import csrf_exempt
from sentry_sdk import Hub

from .forms import ImportForm
from .management.commands.fetch import Command as Fetch
from . import context_processors as cps

DATA = settings.DATA


def export(request, format: str, app_label: str, model_name: str, elements_pk: str):
    pk_list = None if elements_pk == "all" else elements_pk.split(",")
    serializer = get_serializer(format)()

    # Determine file extension
    for ext, module in _serializers.items():
        if module.__name__ == serializer.__module__:
            extension = ext
            break
    else:
        extension = "txt"
    if extension == "python":
        extension = "py"

    if app_label == "all" and model_name == "all":
        # Export all models from all apps
        all_models = apps.get_models()
    elif model_name == "all":
        # Export all models from a given app
        all_models = apps.get_app_config(app_label).get_models()
    else:
        # Export a single model as before
        all_models = [get_object_or_404(ContentType, app_label=app_label, model=model_name).model_class()]

    all_querysets = []
    for model in all_models:
        # Exclude some auto-generated models
        if model._meta.label.lower() in (
            "admin.logentry",
            "auth.permission",
            "contenttypes.contenttype",
            "easy_thumbnails.source",
            "easy_thumbnails.thumbnail",
            "sessions.session",
        ):
            continue
        if not has_permission(request, model):
            continue
        queryset = model.objects.all()
        if pk_list:
            queryset = queryset.filter(pk__in=pk_list)
        all_querysets.append(queryset)

    if not all_querysets:
        raise Http404

    filename = f"export_{app_label}_{model_name}_{dt.datetime.now().strftime('%Y%m%d_%H%M%S')}.{extension}"
    response = HttpResponse()
    response.headers["Content-Type"] = mimetypes.guess_type(f"x.{extension}")[0]
    response.headers["Content-Disposition"] = "attachment; " + _encode_filename(filename)
    serializer.serialize(
        chain.from_iterable(list(qs) for qs in all_querysets),
        stream=response,
        use_natural_foreign_keys=True,
        use_natural_primary_keys=True,
    )
    return response

# serializer.serialize(queryset, stream=response, use_natural_foreign_keys=True, use_natural_primary_keys=True)

def google(_request, id):
    """Return the Google site verification file."""
    if os.getenv("GOOGLE_SITE_VERIFICATION_ID", "") == id:
        return HttpResponse(f"google-site-verification: google{os.getenv('GOOGLE_SITE_VERIFICATION_ID')}.html")
    google_file = DATA / f"google{id}.html"
    """Return the Google site verification file."""
    if os.getenv("GOOGLE_SITE_VERIFICATION_ID", "") == id:
        return HttpResponse(f"google-site-verification: google{os.getenv('GOOGLE_SITE_VERIFICATION_ID')}.html")
    if google_file.exists():
        return FileResponse(google_file.open("rb"))
    raise Http404()


def import_(request):
    if request.method == "POST":
        form = ImportForm(request.POST, request.FILES)
        if form.is_valid():
            for file in form.cleaned_data["files"]:
                format = file.name.split(".")[-1]
                objs_with_deferred_fields = []

                for obj in deserialize(format, file, handle_forward_references=True):
                    obj.save()
                    if obj.deferred_fields is not None:
                        objs_with_deferred_fields.append(obj)

                for obj in objs_with_deferred_fields:
                    obj.save_deferred_fields()

            return HttpResponse("OK")
    else:
        form = ImportForm()
    return render(request, "import.html", {"form": form})


DEBUG_ENGINE = Engine(
    dirs=[str(Path(__file__).parent / "templates")],
    debug=True,
    libraries={
        "i18n": "django.templatetags.i18n",
        "nav": "cate.templatetags.nav",
        "static": "django.templatetags.static",
    },
)


def _render_for_status(request, status, context=None):
    dirs = DEBUG_ENGINE.dirs
    base_template = "cate/site_base.html"

    app_name = request.resolver_match.app_name if request.resolver_match else ""
    if app_name:
        dir = settings.BASE_DIR / app_name / "templates"
        if (dir / app_name / "page_base.html").exists():
            base_template = f"{app_name}/page_base.html"
            dirs.append(dir)

    template = DEBUG_ENGINE.get_template(f"cate/{status}.html")
    DEBUG_ENGINE.dirs = dirs

    djdt_logo = '<span class="djdt-logo"><span>D</span><span>j</span>DT</span>'
    djdt_script = """\
<script>
$(function() {
	console.log("load");
	$(".djdt-logo").click(djdt.show_toolbar);
});
</script>
"""
    djdt_message = (
        SafeString(
            djdt_script
            + "<p>"
            + _("You have the permission to view the error details!")
            + "<br>"
            # Translators: %(djdt)s is the DjDT logo
            + _("Open the debug toolbar (%(djdt)s at top-right) and click on the Error tab.") % {"djdt": djdt_logo}
            + "</p>"
        )
        if request.user.has_perm("can_see_debug_toolbar")
        else ""
    )  # type: ignore

    context = RequestContext(
        request,
        {
            "base_template": base_template,
            "djdt_message": djdt_message,
            **(context or {}),
        },
        processors=[
            django_cps.request,  # for the navbar
            cps.app_name,
        ],
        use_l10n=False,
    )  # type: ignore

    return HttpResponse(template.render(context), status=status)


def handler_404(request: HttpRequest, *args, **kwargs):
    """
    404 (not found) error page.
    """
    return _render_for_status(request, 404)


def handler_500(request: HttpRequest, _template_name=None):
    """
    500 (server error) page that logs the error.
    """
    return _render_for_status(
        request,
        500,
        {
            "error_id": Hub.current.scope.last_event_id() or "?",
        },
    )


def account_index(request):
    return render(request, "account/index.html")


@csrf_exempt
def reload_website(request: HttpRequest):
    forbidden = HttpResponseForbidden("Permission denied.")

    def run_fetch():
        try:
            ret = Fetch().handle(pipe=True)
        except:
            return HttpResponseServerError("Failed to fetch changes")
        return HttpResponse(ret, "text/plain")

    if request.user.is_superuser:  # type: ignore
        return run_fetch()

    if request.method != "POST":
        return HttpResponseNotAllowed(["GET", "POST"])

    # Verify if request came from GitHub
    forwarded_for = request.headers.get("X-Forwarded-For")
    if not forwarded_for:
        return forbidden
    client_ip_address = ip_address(forwarded_for)
    whitelist = requests.get("https://api.github.com/meta").json()["hooks"]

    for valid_ip in whitelist:
        if client_ip_address in ip_network(valid_ip):
            break
    else:
        return forbidden

    # Verify the request signature
    header_signature = request.headers.get("X-Hub-Signature")
    if header_signature is None:
        return forbidden

    sha_name, signature = header_signature.split("=")
    if sha_name != "sha1":
        return HttpResponseServerError("Operation not supported.", status=501)

    mac = hmac.new(force_bytes(settings.GITHUB_WEBHOOK_KEY), msg=force_bytes(request.body), digestmod=sha1)
    if not hmac.compare_digest(force_bytes(mac.hexdigest()), force_bytes(signature)):
        return forbidden

    # If request reached this point we are in a good shape
    # Process the GitHub events
    event = request.headers.get("X-Github-Event", "ping")

    if event == "ping":
        return HttpResponse("pong")
    elif event == "push":
        return run_fetch()

    # In case we receive an event that's not ping or push
    return HttpResponse(status=204)


def robots(_request):
    robots_file = Path(__file__).resolve().parent.parent / "robots.txt"
    if robots_file.exists():
        return FileResponse(robots_file.open("rb"))
    raise Http404()


def upload_image(request: HttpRequest):
    referer_url: str = request.headers["Referer"]
    referer = urlparse(referer_url)
    admin_index = resolve_url("admin:index").rstrip("/") + "/"
    if not referer.path.startswith(admin_index):
        return HttpResponseForbidden("The referer URL is not an admin URL." if settings.DEBUG else "")

    parts = referer.path.removeprefix(admin_index).split("/")
    if len(parts) < 3:
        return HttpResponseForbidden("The referer URL doesn't contain enough information." if settings.DEBUG else "")

    model = apps.get_model(parts[0], parts[1])
    image_model: Type[ImageBase] = apps.get_model(parts[0], parts[1] + "Image")  # type: ignore

    instance = model.objects.get(pk=parts[2])
    image = image_model.objects.create(page=instance, image=request.FILES["file"])

    return JsonResponse({"location": image.image.url})
