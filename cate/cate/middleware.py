import re
from typing import Callable

from django.conf import settings


class SpacelessMiddleware:
	"""
	Trim spaces between tags if not in debug mode
	"""
	def __init__(self, get_response: Callable) -> None:
		self.get_response = get_response

	def __call__(self, request):
		response = self.get_response(request)
		content = response.content
		content = re.sub(rb"\n\s*\n", b"\n", content)
		if not settings.DEBUG:
			content = re.sub(rb">\s+<", b"><", content)
			content = re.sub(rb"^\s+<", b"<", content)
		response.content = content
		return response
