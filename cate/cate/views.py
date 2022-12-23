import hmac
import sys
from hashlib import sha1
from ipaddress import ip_address, ip_network
from pathlib import Path

import requests
from django.conf import settings
from django.http import HttpRequest, HttpResponse, HttpResponseForbidden, HttpResponseNotAllowed, HttpResponseServerError
from django.shortcuts import render
from django.utils.encoding import force_bytes
from django.views.decorators.csrf import csrf_exempt

try:
	sys.path.insert(0, str(Path(__file__).resolve().parent.parent.parent / "scripts"))
	from fetch import fetch  # type: ignore
except ImportError:
	fetch = None

def home(request: HttpRequest):
    return render(request, "cate/home.html")

@csrf_exempt
def reload_website(request: HttpRequest):
	forbidden = HttpResponseForbidden("Permission denied.")
	if not fetch:
		return forbidden

	if request.user.is_superuser: # type: ignore
		fetch()
		return HttpResponse("success")

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
		try:
			fetch()
		except:
			return HttpResponseServerError("Failed to fetch changes")
		return HttpResponse("success")

	# In case we receive an event that's not ping or push
	return HttpResponse(status = 204)
