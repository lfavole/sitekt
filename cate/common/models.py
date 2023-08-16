from datetime import date
from typing import Any, Callable, Type

from django.apps import apps
from django.core.cache import cache
from django.core.exceptions import ValidationError
from django.db import DatabaseError, models
from django.db.models import Manager
from django.urls import reverse
from django.utils.timezone import now
from django.utils.translation import gettext_lazy as _
from storage.fields import FileField, ImageField

from cate.utils.text import slugify

from .fields import DatalistField


class Year(models.Model):
	"""
	A school year to be linked to childs, etc.

	It can be active (or not).
	"""
	start_year = models.fields.IntegerField(_("Start year"), unique = True)
	is_active = models.fields.BooleanField(_("Active year"))

	class Meta:
		verbose_name = _("school year")
		ordering = ["-start_year"]

	def _get_end_year(self):
		return self.start_year + 1
	_get_end_year.short_description = _("End year")
	end_year = property(_get_end_year)

	def _get_formatted_year(self):
		return f"{self.start_year}-{self.end_year}"
	_get_formatted_year.short_description = _("School year") # type: ignore
	formatted_year = property(_get_formatted_year)

	def __str__(self):
		return _("School year %s") % (self.formatted_year,)

	def save(self, *args, **kwargs):
		# Note: we avoid saving the objects to avoid recursion error
		obj = type(self).objects.all()
		if self.is_active:
			# this year becomes an active year => deactivate the other years
			for year in obj.filter(is_active = True):
				if year == self:
					continue
				if not year.is_active:
					continue # avoid hitting the database
				year.is_active = False
				year.save()

		elif not obj.filter(is_active = True).exists():
			# no active years => activate the first year or this year
			first = obj.first()
			if first and not first.is_active: # activate the first year
				first.is_active = True
				first.save()
			else: # one year => this year is active
				self.is_active = True

		super().save(*args, **kwargs)

	def delete(self, *args, **kwargs):
		obj = type(self).objects.all()
		if not obj.filter(is_active = True).exists():
			years = obj.filter(is_active = False)
			if years.exists():
				el = years[0]
				if not el.is_active: # activate the first year
					# we avoid saving the objects to avoid recursion error
					el.is_active = True
					el.save()
			# we are deleting the only active year
			# there will be bugs...

		return super().delete(*args, **kwargs)

	@classmethod
	def get_current(cls):
		"""
		Return the current year.
		"""
		year = cache.get("current_year")
		if not year:
			try:
				year = cls.objects.get(is_active = True)
			except (cls.DoesNotExist, DatabaseError):
				return Year(start_year = date.today().year, is_active = True)
			cache.set("current_year", year)
		return year


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
		slug_candidate = slug_original = slugify(value)
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

class ImageBase(models.Model):
	"""
	Base class for images in pages and articles.
	"""
	image = ImageField(_("Image"))
	page: "models.ForeignKey[CommonPage]"

	def __str__(self):
		return _("Image '%s' in %s") % (self.image.url, self.page)

	class Meta:
		abstract = True

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

class CommonPageImage(ImageBase):
	"""
	Common page image class for all apps.
	"""
	page = models.ForeignKey("Page", on_delete = models.CASCADE, verbose_name = _("Page"))

	class Meta:
		verbose_name = _("page image")
		verbose_name_plural = _("page images")
		abstract = True

class CommonArticle(PageBase):
	"""
	Common article class for all apps.
	"""
	date = models.fields.DateField(_("Date"), default = now)
	hidden = models.fields.BooleanField(_("Hidden article"), default = False)

	class Meta:
		verbose_name = _("article")
		abstract = True
		ordering = ["-date"]

class CommonArticleImage(ImageBase):
	"""
	Common article image class for all apps.
	"""
	page = models.ForeignKey("Article", on_delete = models.CASCADE, verbose_name = _("Article"))

	class Meta:
		verbose_name = _("article image")
		verbose_name_plural = _("article images")
		abstract = True

class CommonGroup(models.Model):
	"""
	Common group class for all apps.
	"""
	name = models.fields.CharField(_("Name"), max_length = 100)

	def __str__(self):
		return self.name

	class Meta:
		verbose_name = _("group")
		abstract = True

class CommonChild(models.Model):
	"""
	Common child class for all apps.
	"""
	nom = models.CharField("Nom de famille", max_length = 100)
	prenom = models.CharField("Prénom", max_length = 100)
	date_naissance = models.DateField("Date de naissance")
	lieu_naissance = models.CharField("Lieu de naissance", max_length = 100)
	adresse = models.TextField("Adresse")

	paye = models.CharField("Payé", max_length = 10, default = "non", choices = [
		("non", "Non"),
		("attente", "En attente"),
		("oui", "Oui"),
	])
	signe = models.BooleanField("Signé", default = False)
	groupe = models.ForeignKey("Group", on_delete = models.SET_NULL, verbose_name = "Groupe", blank = True, null = True)
	photo = ImageField("Photo", blank = True, null = True)
	date_inscription = models.DateTimeField("Date et heure d'inscription", auto_now_add=True)

	class Meta:
		verbose_name = _("child")
		ordering = ["nom", "prenom"]
		abstract = True

	def __str__(self):
		return f"{self.prenom} {self.nom}"

	sacraments_checks: dict[str, str] = {}

	def clean(self):
		today = date.today()
		errors = {}

		def add_error(field, error):
			if field not in errors:
				errors[field] = []
			errors[field].append(error)

		def check_not_future(name: str, msg: str):
			date: "date" | None = getattr(self, name)
			if date and date > today:
				add_error(name, f"{msg.capitalize()} ne doit pas être dans le futur.")

		def check_after_birth(name: str, msg: str):
			date = getattr(self, name)
			if date and date < self.date_naissance:
				add_error(name, f"{msg.capitalize()} doit être après la date de naissance.")

		def check_sacrament(name: str, msg: str):
			if not getattr(self, name):
				return  # the sacrament hasn't been done

			if name == "pardon":
				# special case
				if self.annee_pardon and self.annee_pardon > today.year:  # type: ignore
					add_error(f"annee_{name}", f"L'année {msg} ne doit pas être dans le futur.")
				return

			check_not_future(f"date_{name}", f"la date {msg}")
			check_after_birth(f"date_{name}", f"la date {msg}")

		check_not_future("date_naissance", "la date de naissance")
		for name, msg in self.sacraments_checks.items():
			check_sacrament(name, msg)

		for field, msg in {"tel_mere": "de la mère", "tel_pere": "du père"}.items():
			length = len(getattr(self, field))
			if length not in (0, 10):
				add_error(field, f"Le numéro de téléphone {msg} est incorrect (il a {length} chiffre{'s' if length >= 2 else ''}).")

		if errors:
			raise ValidationError(errors)

class CommonDate(models.Model):
	start_date = models.fields.DateField(_("Start date"))
	end_date = models.fields.DateField(_("End date"), blank = True, null = True)
	start_time = models.fields.TimeField(_("Start time"), blank = True, null = True)
	end_time = models.fields.TimeField(_("End time"), blank = True, null = True)
	time_text = DatalistField(_("Time (as text)"), max_length = 50, blank = True, form_choices = ("Journée", "Week-end", "Séjour"))
	name = models.fields.CharField(_("Name"), max_length = 100)
	short_name = models.fields.CharField(_("Short name"), max_length = 50, blank = True)
	place = models.fields.CharField(_("Place"), max_length = 100)
	cancelled = models.fields.BooleanField(_("Cancelled"))

	class Meta:
		verbose_name = _("date")
		ordering = ["start_date", "start_time"]
		abstract = True

	def clean(self):
		if self.end_date and self.start_date > self.end_date:
			raise ValidationError({"end_date": _("The end date must be after the start date.")})

		if self.end_time and not self.start_time:
			msg = _("The start time must be specified when the end time is specified.")
			raise ValidationError({"start_time": msg})

		if self.end_time and self.start_time > self.end_time:
			raise ValidationError({"end_time": _("The end time must be after the start time.")})

		if self.start_time and self.end_time and self.time_text:
			msg = _("The start time / end time or the time as text must be specified, not both.")
			raise ValidationError({"start_time": msg, "end_time": msg, "time_text": msg})

	def __str__(self): # pylint: disable=E0307
		return self.name

class CommonMeeting(models.Model):
	"""
	Common meeting class for all apps.
	"""
	Kind: "models.TextChoices"
	kind: "models.CharField[str]"
	date = models.fields.DateField(_("Date"))
	date_item: "models.OneToOneField[CommonDate | None]" = models.OneToOneField("Date", on_delete=models.SET_NULL, verbose_name=_("Date item"), blank=True, null=True)  # type: ignore
	name = models.CharField(_("Name"), blank=True, max_length=100)

	get_childs: Callable[[], Manager[CommonChild]]

	def save(self, *args, **kwargs):
		add = self._state.adding
		super().save(*args, **kwargs)
		if add:
			Attendance: Type[CommonAttendance] = apps.get_model(self._meta.app_label, "Attendance")  # type: ignore
			for child in self.get_childs():
				Attendance.objects.create(child=child, meeting=self, is_present=True, has_warned=False)

	def __str__(self):
		return (
			self.name
			or ("" if not self.date_item else self.date_item.name)
			or self.get_kind_display()  # type: ignore
		)

	class Meta:
		verbose_name = _("meeting")
		abstract = True

class CommonAttendance(models.Model):
	"""
	Common attendance class for all apps.
	"""
	child: "models.ForeignKey[CommonChild]" = models.ForeignKey("Child", on_delete=models.CASCADE, verbose_name=_("Child"))
	meeting: "models.ForeignKey[CommonMeeting]" = models.ForeignKey("Meeting", on_delete=models.CASCADE, verbose_name=_("Meeting"))
	is_present = models.BooleanField(_("Present"))
	has_warned = models.BooleanField(_("Has warned"))

	def __str__(self):
		return _("%s was %s%s") % (
			str(self.child),
			(
				# Translators: use inclusive writing
				_("present")
				if self.is_present
				# Translators: use inclusive writing
				else _("absent")
			),
			(" " + _("and has warned")) if self.has_warned else "",
		)

	class Meta:
		verbose_name = _("attendance")
		abstract = True

class CommonDocumentCategory(models.Model):
	"""
	Common document category class for all apps.
	"""
	title = models.CharField(_("Title"), unique=True, max_length = 100)

	def __str__(self):  # pylint: disable=E0307
		return self.title

	class Meta:
		verbose_name = _("document category")
		verbose_name_plural = _("document categories")
		abstract = True

class CommonDocument(models.Model):
	"""
	Common document class for all apps.
	"""
	title = models.fields.CharField(_("Document title"), max_length = 100)
	file = FileField(_("File"), null = True)
	categories: "models.ManyToManyField[CommonDocumentCategory, Any]" = models.ManyToManyField("DocumentCategory", verbose_name=_("Categories"), blank=True)

	class Meta:
		verbose_name = _("document")
		abstract = True

	def __str__(self): # pylint: disable=E0307
		return self.title
