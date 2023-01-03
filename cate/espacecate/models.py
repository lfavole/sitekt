from datetime import datetime

from django.core.validators import MaxValueValidator, MinValueValidator
from django.db import models
from django.urls import reverse
from uservisit.models import CommonUserVisit
from utils.models import CommonArticle, CommonDocument, CommonPage


class UserVisit(CommonUserVisit):
	"""
	User visit on `espacecate` app.
	"""

class Page(CommonPage):
	"""
	Page on `espacecate` app.
	"""
	def __init__(self, *args, **kwargs):
		super().__init__(*args, **kwargs)
	def get_absolute_url(self):
		return reverse("espacecate:page", args = [self.slug])

class Article(CommonArticle):
	"""
	Article on `espacecate` app.
	"""
	def get_absolute_url(self):
		return reverse("espacecate:article", args = [self.slug])

def get_current_year():
	return datetime.now().year

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
		("PS", "Petite section"),
		("MS", "Moyenne section"),
		("GS", "Grande section"),
		("CP", "CP"),
		("CE1", "CE1"),
		("CE2", "CE2"),
		("CM1", "CM1"),
		("CM2", "CM2"),
	]

	ecole = models.fields.CharField("École", choices = ECOLES, max_length = 15)
	classe = models.fields.CharField("Classe", choices = CLASSES, max_length = 5)
	redoublement = models.fields.BooleanField("Redoublement")

	annees_evf = models.fields.IntegerField("Années d'éveil à la foi", validators = [MinValueValidator(0), MaxValueValidator(4)])
	annees_kt = models.fields.IntegerField("Années de caté", validators = [MinValueValidator(0), MaxValueValidator(3)])

	bapteme = models.fields.BooleanField("Baptême")
	date_bapteme = models.fields.DateField("Date du baptême")
	lieu_bapteme = models.CharField("Lieu du baptême", max_length = 100)

	pardon = models.fields.BooleanField("Sacrement du Pardon")
	annee_pardon = models.fields.IntegerField("Année du Sacrement du Pardon", validators = [MinValueValidator(1970), MaxValueValidator(get_current_year)])

	premiere_communion = models.fields.BooleanField("Première communion")
	date_premiere_communion = models.fields.DateField("Date de la première communion")
	lieu_premiere_communion = models.CharField("Lieu de la première communion", max_length = 100)

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
			"fields": ("ecole", "classe", "redoublement")
		}),
		("Caté", {
			"fields": ("annees_evf", "annees_kt", "bapteme", "date_bapteme", "lieu_bapteme", "pardon", "annee_pardon", "premiere_communion", "date_premiere_communion", "lieu_premiere_communion")
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

class Document(CommonDocument):
	"""
	Document on `espacecate` app.
	"""
