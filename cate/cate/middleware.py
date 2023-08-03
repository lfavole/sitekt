import re
from typing import Callable

from django.conf import settings
from django.http import HttpResponse


class SpacelessMiddleware:
	"""
	Trim spaces between tags if not in debug mode
	"""
	def __init__(self, get_response: Callable) -> None:
		self.get_response = get_response

	def __call__(self, request):
		response: HttpResponse = self.get_response(request)
		if response.headers.get("Content-Type", "").split(";")[0] != "text/html":  # type: ignore
			return response
		try:
			content = response.content
		except AttributeError:  # file response
			return response

		content = re.sub(rb"\n\s*\n", b"\n", content)
		if not settings.DEBUG:
			content = re.sub(rb">\s+<", b"><", content)
			content = re.sub(rb"^\s+<", b"<", content)
		response.content = content
		return response
