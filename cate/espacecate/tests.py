import datetime

from django.core.exceptions import ValidationError
from django.db import models
from django.test import TestCase
from django.utils import timezone
from utils.tests import REMOVED, DefaultArgs

from .models import Date

now = timezone.now()
one_day = datetime.timedelta(days = 1)
one_hour = datetime.timedelta(hours = 1)

def_args = DefaultArgs({
	"name": "Test date",
	"place": "Test place",
	"start_date": now.date(),
	"end_date": now + one_day,
	"start_time": now.date(),
	"end_time": now + one_hour,
	"time_text": "",
	"cancelled": False,
})

def clean(model: models.Model, exclude = None):
	"""
	Clean a model. Same as `model.full_clean()` but the execution is stopped when a `ValidationError` is raised.
	"""
	model.clean_fields(exclude)
	model.clean()
	model.validate_unique(exclude)
	model.validate_constraints(exclude) # type: ignore


class DateModelTests(TestCase):
	"""
	Tests on the `Date` model.
	"""
	def test_normal(self):
		"""
		Normal date
		"""
		date = Date(**def_args())
		try:
			clean(date)
		except ValidationError:
			self.fail("ValidationError raised")

	def test_invalid_date(self):
		"""
		end_date < start_date
		"""
		date = Date(**def_args(start_date = now, end_date = now - one_day))
		with self.assertRaises(ValidationError):
			clean(date)

	def test_only_end_date(self):
		"""
		start_date = ?
		end_date = ...
		"""
		date = Date(**def_args(start_date = REMOVED, end_date = now))
		with self.assertRaises(ValidationError):
			clean(date)

	def test_invalid_time(self):
		"""
		end_time < start_time
		"""
		date = Date(**def_args(start_time = now, end_time = now - one_hour))
		with self.assertRaises(ValidationError):
			clean(date)

	def test_only_end_time(self):
		"""
		start_time = ?
		end_time = ...
		"""
		date = Date(**def_args(start_time = REMOVED, end_time = now))
		with self.assertRaises(ValidationError):
			clean(date)

	def test_no_time(self):
		"""
		start_time = ?
		end_time = ?
		time_text = ?
		"""
		date = Date(**def_args(start_time = REMOVED, end_time = REMOVED, time_text = REMOVED))
		with self.assertRaises(ValidationError):
			clean(date)

	def test_all_time_fields(self):
		"""
		start_time = ...
		end_time = ...
		time_text = ...
		"""
		date = Date(**def_args(time_text = "..."))
		with self.assertRaises(ValidationError):
			clean(date)
