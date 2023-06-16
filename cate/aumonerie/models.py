from datetime import date, datetime
from typing import Callable

from common.models import CommonArticle, CommonDate, CommonDocument, CommonDocumentCategory, CommonPage
from django.core.exceptions import ValidationError
from django.core.validators import MinValueValidator
from django.db import models
from django.urls import reverse
from django.utils.translation import gettext_lazy as _
from uservisit.models import CommonUserVisit


class UserVisit(CommonUserVisit):
	"""
	User visit on `aumonerie` app.
	"""

class Page(CommonPage):
	"""
	Page on `aumonerie` app.
	"""
	def __init__(self, *args, **kwargs):
		super().__init__(*args, **kwargs)
	def get_absolute_url(self):
		return reverse("aumonerie:page", args = [self.slug])

class Article(CommonArticle):
	"""
	Article on `aumonerie` app.
	"""
	def get_absolute_url(self):
		return reverse("aumonerie:article", args = [self.slug])

class Child(models.Model):
	"""
	A subscribed child.
	"""
	nom = models.CharField("Nom de famille", max_length = 100)
	prenom = models.CharField("Prénom", max_length = 100)
	date_naissance = models.DateField("Date de naissance")
	lieu_naissance = models.CharField("Lieu de naissance", max_length = 100)
	adresse = models.TextField("Adresse")

	ECOLES = [
		("FARANDOLE", "École La Farandole"),
		("SOLDANELLE", "École La Soldanelle"),
		("PASTEUR", "École Pasteur"),
		("CEZANNE", "École Cézanne"),
		("BARATIER", "École de Baratier"),
		("CHATEAUROUX", "École de Châteauroux"),
		("ST_ANDRE", "École de Saint-André"),
		("CROTS", "École de Crots"),
		("SAVINES", "École de Savines"),
		("ORRES", "École des Orres"),
		("PUYS", "École des Puys"),
		("MAISON", "École à la maison"),
	]

	CLASSES = [
		("6e", "6ème"),
		("5e", "5ème"),
		("4e", "4ème"),
		("3e", "3ème"),
		("2nde", "2nde"),
		("1ere", "1ère"),
		("terminale", "Terminale"),
	]

	ecole = models.fields.CharField("École", choices = ECOLES, max_length = 15)
	classe = models.fields.CharField("Classe", choices = CLASSES, max_length = 10)

	bapteme = models.fields.BooleanField("Baptême")
	date_bapteme = models.fields.DateField("Date du baptême")
	lieu_bapteme = models.CharField("Lieu du baptême", max_length = 100)

	premiere_communion = models.fields.BooleanField("Première communion")
	date_premiere_communion = models.fields.DateField("Date de la première communion")
	lieu_premiere_communion = models.CharField("Lieu de la première communion", max_length = 100)

	profession = models.fields.BooleanField("Profession de foi")
	date_profession = models.fields.DateField("Date de la profession de foi")
	lieu_profession = models.CharField("Lieu de la profession de foi", max_length = 100)

	confirmation = models.fields.BooleanField("Confirmation")
	date_confirmation = models.fields.DateField("Date de la Confirmation")
	lieu_confirmation = models.CharField("Lieu de la Confirmation", max_length = 100)

	nom_pere = models.CharField("Nom et prénom du père", blank = True, max_length = 100)
	adresse_pere = models.TextField("Adresse du père")
	tel_pere = models.CharField("Téléphone du père", max_length = 10)
	email_pere = models.EmailField("Email du père", max_length = 100)

	nom_mere = models.CharField("Nom et prénom de la mère", blank = True, max_length = 100)
	adresse_mere = models.TextField("Adresse de la mère")
	tel_mere = models.CharField("Téléphone de la mère", max_length = 10)
	email_mere = models.EmailField("Email de la mère", max_length = 100)

	freres_soeurs = models.TextField("Frères et soeurs")

	autres_infos = models.TextField("Autres informations")

	photos = models.BooleanField("Publication des photos")
	frais = models.fields.IntegerField("Participation aux frais", validators = [MinValueValidator(0)])

	class Meta:
		verbose_name = "Enfant"

	fieldsets = (
		("Informations de l'enfant", {
			"fields": ("nom", "prenom", "date_naissance", "lieu_naissance", "adresse")
		}),
		("École", {
			"fields": ("ecole", "classe")
		}),
		("Caté", {
			"fields": ("bapteme", "date_bapteme", "lieu_bapteme", "premiere_communion", "date_premiere_communion", "lieu_premiere_communion", "profession", "date_profession", "lieu_profession", "confirmation", "date_confirmation", "lieu_confirmation")
		}),
		("Coordonnées", {
			"fields": ("nom_mere", "adresse_mere", "tel_mere", "email_mere", "nom_mere", "adresse_mere", "tel_mere", "email_mere", "freres_soeurs")
		}),
		("Autres informations", {
			"fields": ("autres_infos",)
		}),
		("Autorisation", {
			"fields": ("photos", "frais")
		}),
	)

	def __str__(self):
		return self.prenom + " " + self.nom

	def clean(self):
		def check_date(operator: Callable[[date, date], bool], base_value: date, name: str, msg: str):
			value: date = getattr(self, name)
			if not operator(value, base_value):
				raise ValidationError({name: msg})

		def before(a, b):
			return a <= b
		def after(a, b):
			return a >= b

		now = datetime.now()
		def check_not_future(name: str, msg: str):
			check_date(before, now, name, msg)

		def check_after_birth(name: str, msg: str):
			check_date(after, self.date_naissance, name, msg)

		template_not_future = "%s ne peut pas être dans le futur."
		template_after_birth = "%s doit être après la date de naissance."

		check_not_future("date_naissance", template_not_future % ("La date de naissance",))
		check_not_future("date_bapteme", template_not_future % ("La date du baptême",))
		check_not_future("date_premiere_communion", template_not_future % ("La date de la première communion",))
		check_not_future("date_profession", template_not_future % ("La date de la profession de foi",))
		check_not_future("date_confirmation", template_not_future % ("La date de la Confirmation",))

		check_after_birth("date_bapteme", template_after_birth % ("La date du baptême",))
		check_after_birth("date_premiere_communion", template_after_birth % ("La date de la première communion",))
		check_after_birth("date_profession", template_after_birth % ("La date de la profession de foi",))
		check_after_birth("date_confirmation", template_after_birth % ("La date de la Confirmation",))

class Date(CommonDate):
	"""
	Date on `aumonerie` app.
	"""

class DocumentCategory(CommonDocumentCategory):
	"""
	Document category on `aumonerie` app.
	"""

class Document(CommonDocument):
	"""
	Document on `aumonerie` app.
	"""
	categories = models.ManyToManyField(DocumentCategory, verbose_name=_("Categories"), blank=True)
