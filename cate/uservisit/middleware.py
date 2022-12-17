# https://github.com/yunojuno/django-user-visit/blob/master/user_visit/middleware.py
import datetime
import importlib
import logging
from typing import Callable, Optional, Type

from django.core.exceptions import MiddlewareNotUsed
from django.db import IntegrityError
from django.db.transaction import atomic
from django.http import HttpRequest, HttpResponse
from django.utils import timezone

from .models import UserVisit
from .settings import DUPLICATE_LOG_LEVEL, RECORDING_BYPASS, RECORDING_DISABLED

logger = logging.getLogger(__name__)

@atomic
def save_user_visit(user_visit) -> None:
	"""Save the user visit and handle db.IntegrityError."""
	try:
		user_visit.save()
	except IntegrityError:
		getattr(logger, DUPLICATE_LOG_LEVEL)(
			"Error saving user visit (hash='%s')", user_visit.hash
		)


class UserVisitMiddleware:
	"""Middleware to record user visits."""

	def __init__(self, get_response: Callable) -> None:
		if RECORDING_DISABLED:
			raise MiddlewareNotUsed("UserVisit recording has been disabled")
		self.get_response = get_response

	def __call__(self, request: HttpRequest) -> Optional[HttpResponse]:
		resp = self.get_response(request)
		if request.user.is_staff or RECORDING_BYPASS(request): # type: ignore
			return resp

		request.session.save()

		if not request.resolver_match:
			return resp
		app_name = request.resolver_match.app_name
		if not app_name:
			return resp
		model_name = app_name[0].upper() + app_name[1:].lower()
		try:
			models = importlib.import_module(f"{app_name}.models")
			RealUserVisit: Type[UserVisit] = getattr(models, f"{model_name}UserVisit")
		except (ModuleNotFoundError, AttributeError):
			return resp
		uv = RealUserVisit.objects.create(request, timezone.now())
		uv_objects = RealUserVisit.objects.filter(hash = uv.hash).order_by("-timestamp")
		if not uv_objects.exists() or (uv.timestamp - uv_objects[0].timestamp) >= datetime.timedelta(seconds = 1800):
			save_user_visit(uv)

		return resp
