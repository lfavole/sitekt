from datetime import datetime

from django.core.validators import MaxValueValidator, MinValueValidator
from django.db import models
from django.urls import reverse
from django.utils.text import slugify
from uservisit.models import UserVisit, UserVisitManager


class EspacecateUserVisit(UserVisit):
	pass

class PageBase(models.Model):
	slug = models.fields.SlugField("ID", max_length = 100, editable = False, primary_key = True)
	title = models.fields.CharField("Titre", max_length = 100)
	content = models.fields.TextField("Contenu", blank = True)
	hidden = models.fields.BooleanField("Page cachée", default = False)

	class Meta:
		abstract = True

	def _generate_slug(self):
		max_length = self._meta.get_field("slug").max_length # type: ignore
		value = self.title
		slug_candidate = slug_original = slugify(value, allow_unicode = False)
		i = 0
		while True:
			i += 1
			if not Page.objects.filter(slug = slug_candidate).exists():
				break
			slug_candidate = slug_original + "-" + str(i)

		return slug_candidate

	def save(self, *args, **kwargs):
		if self._state.adding:
			self.slug = self._generate_slug()

		super().save(*args, **kwargs)

	def __str__(self):
		return f"{self.title}"

	def get_absolute_url(self):
		return reverse("espacecate:page", args = [self.slug])

class Page(PageBase):
	order = models.PositiveIntegerField("Ordre", default = 0, null = False)
	parent_page = models.ForeignKey("self", blank = True, null = True, on_delete = models.SET_NULL, verbose_name = "Page précédente")

	class Meta:
		ordering = ["order"]

	def get_absolute_url(self):
		return reverse("espacecate:page", args = [self.slug])

class Article(PageBase):
	hidden = models.fields.BooleanField("Article caché", default = False)

	def get_absolute_url(self):
		return reverse("espacecate:article", args = [self.slug])

class Child(models.Model):
	nom = models.CharField("Nom de famille", max_length = 100)
	prenom = models.CharField("Prénom", max_length = 100)
	date_naissance = models.DateField("Date de naissance")
	lieu_naissance = models.CharField("Lieu de naissance", max_length = 100)
	adresse = models.TextField("Adresse")

	ECOLES = [
		("FARANDOLE", "École La Farandole"),
		("SOLDANELLE", "École La Soldanellle"),
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
	annee_pardon = models.fields.IntegerField("Année du Sacrement du Pardon", validators = [MinValueValidator(1970), MaxValueValidator(datetime.now().year)])

	premiere_communion = models.fields.BooleanField("première communion")
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
		("Informations", {
			"fields": ("first_name", "last_name", "date_of_birth", "place_of_birth", "address")
		}),
		# ('Availability', {
		# 	'fields': ('status', 'due_back')
		# }),
	)

	def __str__(self):
		return self.prenom + " " + self.nom

class Document(models.Model):
	title = models.fields.CharField("Titre du document", max_length = 100)
	file = models.FileField("Document", upload_to = "docs/")

	def __str__(self):
		return self.title
