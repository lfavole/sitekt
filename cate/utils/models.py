from django.core.exceptions import ValidationError
from django.db import models
from django.urls import reverse
from django.utils.text import slugify
from django.utils.timezone import now
from django.utils.translation import gettext_lazy as _
from filer.fields.file import FilerFileField

from .fields import DatalistField


class PageBase(models.Model):
	"""
	Base class for pages and articles.
	"""
	slug = models.fields.SlugField(_("Slug"), max_length = 100, editable = False, primary_key = True)
	title = models.fields.CharField(_("Title"), max_length = 100)
	content = models.fields.TextField(_("Content"), blank = True)
	hidden = models.fields.BooleanField(_("Hidden page"), default = False)

	class Meta:
		abstract = True

	def _generate_slug(self):
		value = self.title
		slug_candidate = slug_original = slugify(value, allow_unicode = False)
		i = 0
		while True:
			i += 1
			if not type(self).objects.filter(slug = slug_candidate).exists(): # type: ignore
				break
			slug_candidate = slug_original + "-" + str(i)

		return slug_candidate

	def save(self, *args, **kwargs):
		if self._state.adding:
			self.slug = self._generate_slug()

		super().save(*args, **kwargs)

	def __str__(self): # pylint: disable=E0307
		return self.title

class CommonPage(PageBase):
	"""
	Common page class for all apps.
	"""
	order = models.PositiveIntegerField(_("Order"), default = 0, null = False)
	parent_page = models.ForeignKey("self", blank = True, null = True, on_delete = models.SET_NULL, verbose_name = _("Previous page"))

	class Meta:
		verbose_name = _("page")
		abstract = True
		ordering = ["order"]

	def get_absolute_url(self):
		return reverse("espacecate:page", args = [self.slug])

class CommonArticle(PageBase):
	"""
	Common article class for all apps.
	"""
	date = models.fields.DateField(_("Date"), default = now)
	hidden = models.fields.BooleanField(_("Hidden article"), default = False)

	class Meta:
		verbose_name = _("article")
		abstract = True

class CommonDate(models.Model):
	start_date = models.fields.DateField(_("Start date"))
	end_date = models.fields.DateField(_("End date"), blank = True)
	start_time = models.fields.TimeField(_("Start time"), blank = True)
	end_time = models.fields.TimeField(_("End time"), blank = True)
	# time_text = models.fields.CharField(_("Time (as text)"), max_length = 50, blank = True)
	# time_text = DatalistField(_("Time (as text)"), max_length = 50, blank = True, choices = (("J", "Journée"), ("W", "Week-end"), ("S", "Séjour")))
	time_text = DatalistField(_("Time (as text)"), max_length = 50, blank = True, form_choices = ("Journée", "Week-end", "Séjour"))
	name = models.fields.CharField(_("Name"), max_length = 100)
	short_name = models.fields.CharField(_("Short name"), max_length = 50, blank = True)
	place = models.fields.CharField(_("Place"), max_length = 100)
	cancelled = models.fields.BooleanField(_("Cancelled"))

	class Meta:
		verbose_name = _("date")
		abstract = True

	def clean(self):
		if self.start_date > self.end_date:
			raise ValidationError({"end_date": _("The end date must be after the start date.")})

		if self.end_time and not self.start_time:
			msg = _("The start time must be specified when the end time is specified.")
			raise ValidationError({"start_time": msg})

		if not self.time_text and not self.start_time:
			msg = _("The time as text or the start time must be specified.")
			raise ValidationError({"start_time": msg, "time_text": msg})

		# do this after because start_time can be None
		if self.start_time > self.end_time:
			raise ValidationError({"end_time": _("The end time must be after the start time.")})

		if not self.start_time and not self.end_time and not self.time_text:
			msg = _("The start time, the end time or the time as text must be specified.")
			raise ValidationError({"start_time": msg, "end_time": msg, "time_text": msg})

		if self.start_time and self.end_time and self.time_text:
			msg = _("The start time / end time or the time as text must be specified, not both.")
			raise ValidationError({"start_time": msg, "end_time": msg, "time_text": msg})

	def __str__(self): # pylint: disable=E0307
		return self.name

class CommonDocument(models.Model):
	"""
	Common document class for all apps.
	"""
	title = models.fields.CharField(_("Document title"), max_length = 100)
	file = FilerFileField(verbose_name = _("File"), null = True, on_delete = models.SET_NULL) # type: ignore

	class Meta:
		verbose_name = _("document")
		abstract = True

	def __str__(self): # pylint: disable=E0307
		return self.title
