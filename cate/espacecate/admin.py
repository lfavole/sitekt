from adminsortable2.admin import SortableAdminMixin
from cate.widgets import MarkdownEditor
from django.contrib import admin
from django import forms
from uservisit.admin import UserVisitAdmin

from .models import Article, Document, Child, EspacecateUserVisit, Page

@admin.register(EspacecateUserVisit)
class EspacecateUserVisitAdmin(UserVisitAdmin):
	pass

class PageAdminForm(forms.ModelForm):
	model = Page
	class Meta:
		fields = "__all__"
		widgets = {
			"content": MarkdownEditor(attrs = {"style": "width: 90%; height: 100%;"}),
		}

@admin.register(Page)
class PageAdmin(SortableAdminMixin, admin.ModelAdmin):
	form = PageAdminForm


class ArticleAdminForm(PageAdminForm):
	model = Article
	class Meta:
		fields = "__all__"
		widgets = {
			"content": MarkdownEditor(attrs = {"style": "width: 90%; height: 100%;"}),
		}

@admin.register(Article)
class ArticleAdmin(admin.ModelAdmin):
	form = ArticleAdminForm


@admin.register(Child)
class EnfantAdmin(admin.ModelAdmin):
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
class DocumentAdmin(admin.ModelAdmin):
	list_display = ["title", "file"]
