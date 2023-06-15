from common.admin import CommonArticleAdmin, CommonDateAdmin, CommonDocumentAdmin, CommonDocumentCategoryAdmin, CommonPageAdmin
from django.contrib import admin
from uservisit.admin import CommonUserVisitAdmin

from .models import Article, Child, Date, Document, DocumentCategory, Page, UserVisit


@admin.register(UserVisit)
class UserVisitAdmin(CommonUserVisitAdmin):
	"""
	Admin interface for user visits of the espacecate app.
	"""

@admin.register(Page)
class PageAdmin(CommonPageAdmin):
	"""
	Admin interface for pages of the espacecate app.
	"""

@admin.register(Article)
class ArticleAdmin(CommonArticleAdmin):
	"""
	Admin interface for articles of the espacecate app.
	"""

@admin.register(Child)
class ChildAdmin(admin.ModelAdmin):
	"""
	Admin interface for childs of the espacecate app.
	"""
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
			"fields": ("nom_pere", "adresse_pere", "tel_pere", "email_pere", "nom_mere", "adresse_mere", "tel_mere", "email_mere", "freres_soeurs")
		}),
		("Autres informations", {
			"fields": ("autres_infos",)
		}),
		("Autorisation", {
			"fields": ("photos", "frais")
		}),
	)

@admin.register(Document)
class DocumentAdmin(CommonDocumentAdmin):
	"""
	Admin interface for documents of the espacecate app.
	"""

@admin.register(DocumentCategory)
class DocumentCategoryAdmin(CommonDocumentCategoryAdmin):
	"""
	Admin interface for document categories of the espacecate app.
	"""

@admin.register(Date)
class DateAdmin(CommonDateAdmin):
	"""
	Admin interface for dates of the espacecate app.
	"""
