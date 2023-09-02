import datetime
from contextlib import contextmanager
from typing import Type
from cate.templatetags.format_date import format_date

from common.tests import REMOVED, DefaultArgs
from django.contrib.auth import get_user_model
from django.contrib.auth.models import Permission, User as DjangoUser
from django.core.exceptions import ValidationError
from django.db import models
from django.shortcuts import resolve_url
from django.test import TestCase
from django.urls import reverse
from django.utils.formats import time_format

from .models import Article, Date

now = datetime.datetime(2023, 1, 1, 12, 0, 0)
one_day = datetime.timedelta(days = 1)
one_hour = datetime.timedelta(hours = 1)

def_args = DefaultArgs({
	"name": "Test date",
	"place": "Test place",
	"start_date": now.date(),
	"end_date": now.date() + one_day,
	"start_time": now.time(),
	"end_time": (now + one_hour).time(),
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
	# https://gist.github.com/hzlmn/6b7bc384301afefcac6de3829bd4c032
	@contextmanager
	def assertValidationOK(self):
		"""
		Fails if the content of the with statement raises a ValidationError.
		"""
		try:
			yield None
		except ValidationError:
			self.fail("ValidationError raised")

	def test_normal(self):
		"""
		Normal date
		"""
		date = Date(**def_args())
		with self.assertValidationOK():
			clean(date)

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
		date = Date(**def_args(start_time = now.time(), end_time = (now - one_hour).time()))
		with self.assertRaises(ValidationError):
			clean(date)

	def test_only_end_time(self):
		"""
		start_time = ?
		end_time = ...
		"""
		date = Date(**def_args(start_time = REMOVED, end_time = now.time()))
		with self.assertRaises(ValidationError):
			clean(date)

	def test_no_time(self):
		"""
		start_time = ?
		end_time = ?
		time_text = ?
		"""
		date = Date(**def_args(start_time = REMOVED, end_time = REMOVED, time_text = REMOVED))
		with self.assertValidationOK():
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

	def test_start_end_date(self):
		"""
		start_date = x
		=> start = x at midnight
		=> end = x + 1 day at midnight
		"""
		for date_to_try in [
			now,  # January 1st
			now - datetime.timedelta(days=1),  # December 31st
			now + datetime.timedelta(days=30),  # January 31st
		]:
			date = Date(start_date = date_to_try.date())
			start = datetime.datetime.combine(date_to_try.date(), datetime.time())
			end = start + datetime.timedelta(days=1)
			self.assertEqual(date.start, start)
			self.assertEqual(date.end, end)

	def test_start_end_time(self):
		"""
		start_date = x
		start_time = y
		=> start = x at y
		=> end = x at y + 1 hour
		"""
		for date_to_try in [
			now,  # January 1st at 12:00
			now - datetime.timedelta(days=1),  # December 31st at 12:00
			now + datetime.timedelta(days=30),  # January 31st at 12:00
			now + datetime.timedelta(hours=11, minutes=30),  # January 1st at 23:30 (day overflow)
			datetime.datetime.combine(now.date(), datetime.time()),  # January 1st at 00:00
		]:
			date = Date(start_date = date_to_try.date(), start_time = date_to_try.time())
			start = date_to_try
			end = start + datetime.timedelta(hours=1)
			self.assertEqual(date.start, start)
			self.assertEqual(date.end, end)

	def test_past(self):
		"""
		start = now - 1 day => past
		start = now - 1 hour - 5 seconds => past*

		start = now => current
		start = now - 50 minutes => current

		start = now + 5 seconds => future*

		Also checks that the 2 other attributes are false.

		* avoids race conditions
		"""
		now = datetime.datetime.now()
		past_checks = [
			now - datetime.timedelta(days=1),
			now - datetime.timedelta(hours=1, seconds=5),
		]
		current_checks = [
			now,
			now - datetime.timedelta(minutes=50),
		]
		future_checks = [
			now + datetime.timedelta(seconds=5),
			now + datetime.timedelta(days=1),
		]

		for date_to_try in past_checks:
			date = Date(start_date = date_to_try.date(), start_time = date_to_try.time())
			self.assertTrue(date.is_past)

			self.assertFalse(date.is_current)
			self.assertFalse(date.is_future)

		for date_to_try in current_checks:
			date = Date(start_date = date_to_try.date(), start_time = date_to_try.time())
			self.assertTrue(date.is_current)

			self.assertFalse(date.is_past)
			self.assertFalse(date.is_future)

		for date_to_try in future_checks:
			date = Date(start_date = date_to_try.date(), start_time = date_to_try.time())
			self.assertTrue(date.is_future)

			self.assertFalse(date.is_past)
			self.assertFalse(date.is_current)

class DateTests(TestCase):
	"""
	Tests on the dates page.
	"""
	def test_no_dates(self):
		"""
		No dates => "Aucune date" in the page
		"""
		response = self.client.get(reverse("espacecate:dates"))
		self.assertEqual(response.status_code, 200)
		self.assertContains(response, "Aucune date")
		self.assertQuerysetEqual(response.context["dates"], [])

	def test_one_date(self):
		"""
		A date is shown in the page
		"""
		date = Date.objects.create(**def_args())

		response = self.client.get(reverse("espacecate:dates"))
		self.assertEqual(response.status_code, 200)
		self.assertContains(response, format_date(date.start_date, date.end_date))
		self.assertContains(response, time_format(date.start_time, "G:i"))  # type: ignore
		self.assertContains(response, "– " + time_format(date.end_time, "G:i"))  # type: ignore
		self.assertQuerysetEqual(response.context["dates"], [date])

class ArticlesTests(TestCase):
	"""
	Tests on the articles.
	"""
	def test_no_articles(self):
		"""
		No articles => "Aucun article" in the list page
		"""
		response = self.client.get(reverse("espacecate:articles"))
		self.assertEqual(response.status_code, 200)
		self.assertContains(response, "Aucun article")
		self.assertQuerysetEqual(response.context["articles"], [])

	def test_one_article(self):
		"""
		An article is shown in the list
		"""
		article = Article.objects.create(title = "Test article", content = "The content of the article...", date = now)

		response = self.client.get(reverse("espacecate:articles"))
		self.assertEqual(response.status_code, 200)
		self.assertContains(response, article.title)
		self.assertQuerysetEqual(response.context["articles"], [article])

		response = self.client.get(resolve_url(article))
		self.assertEqual(response.status_code, 200)

	def test_hidden_article(self):
		"""
		A hidden article isn't shown in the list
		"""
		article = Article.objects.create(title = "Test article", content = "The content of the article...", date = now, hidden = True)

		response = self.client.get(reverse("espacecate:articles"))
		self.assertEqual(response.status_code, 200)
		self.assertContains(response, "Aucun article")
		self.assertQuerysetEqual(response.context["articles"], [])

		response = self.client.get(resolve_url(article))
		self.assertEqual(response.status_code, 404)

	def test_future_article(self):
		"""
		A future article isn't shown in the list
		"""
		article = Article.objects.create(title = "Test article", content = "The content of the article...", date = datetime.datetime.now() + one_day)

		response = self.client.get(reverse("espacecate:articles"))
		self.assertEqual(response.status_code, 200)
		self.assertContains(response, "Aucun article")
		self.assertQuerysetEqual(response.context["articles"], [])

		response = self.client.get(resolve_url(article))
		self.assertEqual(response.status_code, 404)

	def prepare_user(self):
		user = get_user_model().objects.create_user("lfavole")
		# view_articles = Permission.objects.get(name="Can view article")
		view_articles = Permission.objects.get_by_natural_key("view_article", "espacecate", "article")
		user.user_permissions.add(view_articles)
		self.client.force_login(user)

	def test_admin_hidden_article(self):
		"""
		The admins can see the hidden articles.
		They are displayed in the list with "Article caché" message.
		"""
		self.prepare_user()
		article = Article.objects.create(title = "Test article", content = "The content of the article...", hidden = True)

		response = self.client.get(reverse("espacecate:articles"))
		self.assertEqual(response.status_code, 200)
		self.assertContains(response, "Article caché")

		response = self.client.get(resolve_url(article))
		self.assertEqual(response.status_code, 200)
		self.assertContains(response, article.content)

	def test_admin_empty_article(self):
		"""
		The admins can see the empty articles in the list with "Article vide" message.
		"""
		self.prepare_user()
		article = Article.objects.create(title = "Test article", content = "")

		response = self.client.get(reverse("espacecate:articles"))
		self.assertEqual(response.status_code, 200)
		self.assertContains(response, "Article vide")

		response = self.client.get(resolve_url(article))
		self.assertEqual(response.status_code, 200)
		self.assertContains(response, article.title)

	def test_admin_future_article(self):
		"""
		The admins can see the future articles in the list with "Article futur" message.
		"""
		self.prepare_user()
		article = Article.objects.create(title = "Test article", content = "The content of the article...", date = datetime.datetime.now() + one_day)

		response = self.client.get(reverse("espacecate:articles"))
		self.assertEqual(response.status_code, 200)
		self.assertContains(response, "Article futur")

		response = self.client.get(resolve_url(article))
		self.assertEqual(response.status_code, 200)
		self.assertContains(response, article.content)
