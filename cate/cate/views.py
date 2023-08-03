import datetime as dt
import hmac
import importlib
import sys
from hashlib import sha1
from ipaddress import ip_address, ip_network
from pathlib import Path
from typing import Type
from urllib.parse import quote, urlparse

import requests
from common.models import ImageBase
from common.views import _encode_filename, has_permission
from django.apps import apps
from django.conf import settings
from django.contrib.contenttypes.models import ContentType
from django.core.serializers import get_serializer
from django.http import FileResponse, Http404, HttpRequest, HttpResponse, HttpResponseForbidden, HttpResponseNotAllowed, HttpResponseServerError, JsonResponse
from django.shortcuts import get_object_or_404, render, resolve_url
from django.template import Context, Engine
from django.utils.encoding import force_bytes
from django.views.debug import ExceptionReporter, technical_404_response
from django.views.decorators.csrf import csrf_exempt
from errors.models import Error

DATA = Path(__file__).resolve().parent.parent.parent / "data"

fetch_cache = None

def get_fetch_function():
	global fetch_cache

	if fetch_cache is not None:
		return fetch_cache

	try:
		sys.path.insert(0, str(Path(__file__).resolve().parent.parent.parent))
		fetch_cache = importlib.import_module("scripts.fetch", "scripts").fetch
	except ImportError:
		fetch_cache = None

	return fetch_cache

def export(request, format: str, app_label: str, model_name: str, elements_pk: str):
	# Run the operations that don't need the database first
	pk_list = None if elements_pk == "all" else [int(pk) for pk in elements_pk.split(",")]
	serializer = get_serializer(format)()

	# import this now because it is assigned during serializers loading
	from django.core.serializers import _serializers
	for ext, module in _serializers:
		if module == serializer.__module__:
			extension = ext
			break
	else:
		extension = "txt"

	content_type = get_object_or_404(ContentType, app_label=app_label, model=model_name)
	model = content_type.model_class()

	if not model:
		raise Http404

	# Check for permission
	if not has_permission(request, model):
		if not settings.DEBUG:
			raise Http404
		return HttpResponseForbidden("Permission denied.")

	queryset = model.objects.all()
	if pk_list:
		queryset = queryset.filter(pk__in=pk_list)

	response = HttpResponse()

	date = dt.datetime.now().strftime("%Y%m%d_%H%M%S")
	filename = f"export_{content_type.app_label}_{content_type.model}_{date}.{extension}"
	response.headers["Content-Disposition"] = "attachment; " + _encode_filename(filename)

	serializer.serialize(queryset, stream=response)
	return response

def google(_request, id):
    google_file = DATA / f"google{id}.html"
    if google_file.exists():
        return FileResponse(google_file.open("rb"))
    raise Http404()

def home(request: HttpRequest):
    return render(request, "cate/home.html", {"app": "home"})


def handler_404(request, exception):
    """
    404 (not found) error page.
    """
    if request.user and request.user.has_perm("can_see_traceback"):
        return technical_404_response(request, exception)
    return render(
        request,
        "website/404.html",
        {
            "request_path": quote(request.path),
            # "exception": exception_repr,
        },
        status=404,
    )


DEBUG_ENGINE = Engine(
    dirs=[str(Path(__file__).parent / "templates")],
    debug=True,
    libraries={
        "i18n": "django.templatetags.i18n",
        "nav": "cate.templatetags.nav",
        "static": "django.templatetags.static",
    },
)


def handler_500(request, _template_name=None):
    """
    500 (server error) page that logs the error.
    """
    reporter = ExceptionReporter(request, *sys.exc_info(), is_email=True)
    html = reporter.get_traceback_html()
    error = Error.create_from_traceback_data(reporter.get_traceback_data(), html)
    if request.user and request.user.has_perm("can_see_traceback"):
        return HttpResponse(html, status=500)

    with (Path(__file__).parent / "templates/cate/500.html").open() as f:
        t = DEBUG_ENGINE.from_string(f.read())
    c = Context({"error_id": error.pk}, use_l10n=False)
    html = t.render(c)
    return HttpResponse(html, status=500)


@csrf_exempt
def reload_website(request: HttpRequest):
	forbidden = HttpResponseForbidden("Permission denied.")
	fetch = get_fetch_function()
	if not fetch:
		return forbidden

	def run_fetch():
		try:
			ret = fetch(pipe = True)
		except:
			return HttpResponseServerError("Failed to fetch changes")
		return HttpResponse(ret, "text/plain")

	if request.user.is_superuser: # type: ignore
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
		return HttpResponseServerError("Operation not supported.", status = 501)

	mac = hmac.new(force_bytes(settings.GITHUB_WEBHOOK_KEY), msg = force_bytes(request.body), digestmod = sha1)
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
	return HttpResponse(status = 204)

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

	instance = model.objects.get(pk = parts[2])
	image = image_model.objects.create(page = instance, image = request.FILES["file"])

	return JsonResponse({"location": image.image.url})
