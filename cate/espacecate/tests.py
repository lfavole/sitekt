import datetime

from django.core.exceptions import ValidationError
from django.db import models
from django.test import TestCase
from django.urls import reverse
from utils.tests import REMOVED, DefaultArgs

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

class ArticlesListTests(TestCase):
	"""
	Tests on the articles list page.
	"""
	def test_no_articles(self):
		"""
		No articles => "Aucun article" in the page
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

	def test_hidden_article(self):
		"""
		A hidden article isn't shown in the list
		"""
		_article = Article.objects.create(title = "Test article", content = "The content of the article...", date = now, hidden = True)
		response = self.client.get(reverse("espacecate:articles"))
		self.assertEqual(response.status_code, 200)
		self.assertContains(response, "Aucun article")
		self.assertQuerysetEqual(response.context["articles"], [])

	def test_future_article(self):
		"""
		A future article isn't shown in the list
		"""
		_article = Article.objects.create(title = "Test article", content = "The content of the article...", date = datetime.datetime.now() + one_day)
		response = self.client.get(reverse("espacecate:articles"))
		self.assertEqual(response.status_code, 200)
		self.assertContains(response, "Aucun article")
		self.assertQuerysetEqual(response.context["articles"], [])
