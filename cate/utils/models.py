from django.db import models
from django.urls import reverse
from django.utils.text import slugify
from django.utils.timezone import now
from django.utils.translation import gettext_lazy as _
from filer.fields.file import FilerFileField


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

	def __str__(self):
		return f"{self.title}"

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

class CommonDocument(models.Model):
	"""
	Common document class for all apps.
	"""
	title = models.fields.CharField(_("Document title"), max_length = 100)
	file = FilerFileField(verbose_name = _("File"), null = True, on_delete = models.SET_NULL) # type: ignore

	def __str__(self): # pylint: disable=E0307
		return self.title

	class Meta:
		verbose_name = _("document")
		abstract = True
