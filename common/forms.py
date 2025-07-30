import copy

from django import forms
from django.db import models
from django.forms import CheckboxSelectMultiple
from django.utils.safestring import mark_safe
from django.utils.translation import gettext_lazy as _

from .fields import DisplayedHTMLField
from .models import Child, Date, Group, LastChildVersion, Year


class BooleanField(forms.BooleanField):
    """
    Boolean field with yes/no radio buttons.
    """

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.widget = forms.RadioSelect(
            attrs={"required": True},
            choices=[(True, "Oui"), (False, "Non")],
        )
        self.widget.is_required = True

    def to_python(self, value):
        if value is None:
            return None
        return super().to_python(value)

    def validate(self, value):
        if value is None:
            raise forms.ValidationError(self.error_messages["required"], code="required")
        super().validate(value)


def formfield_for_dbfield(db_field, **kwargs):
    if isinstance(db_field, models.DateField):
        kwargs["widget"] = forms.DateInput(
            format="%Y-%m-%d",
            attrs={"type": "date"},
        )
    if isinstance(db_field, models.BooleanField):
        kwargs["form_class"] = BooleanField
    return db_field.formfield(**kwargs)

class SubscriptionForm(forms.Form):
    autorisation = DisplayedHTMLField(
        "Un document intitulé <b>« Autorisation et engagement »</b> devra être signé par vos soins.<br>"
        "Après avoir terminé l'inscription, vous pourrez le télécharger, "
        "l'imprimer, le compléter, le signer et nous le rapporter à la prochaine rencontre du catéchisme, "
        "sinon une version papier vous sera donnée."
    )

    fieldsets_template = "common/form_as_fieldsets.html"

    def as_fieldsets(self):
        """Render as <fieldset> elements."""
        return self.render(self.fieldsets_template)  # type: ignore

    def as_fieldsets_with_numbers(self):
        """Render as <fieldset> elements."""
        return self.render(self.fieldsets_template, {**self.get_context(), "numbers": True})  # type: ignore

    def save(self, request):
        child = Child()

        for f in Child._meta.fields:
            if f.name not in self.fields:
                continue
            # Leave defaults for fields that aren't in POST data, except for
            # checkbox inputs because they don't appear in POST data if not checked.
            if (
                f.has_default()
                and self[f.name].field.widget.value_omitted_from_data(
                    self.data, self.files, self.add_prefix(f.name)
                )  # type: ignore
                and self.cleaned_data.get(f.name) in self[f.name].field.empty_values
            ):
                continue
            f.save_form_data(child, self.cleaned_data[f.name])

        child.group = child.get_assigned_group()
        child.user = request.user

        child.save()
        return child

    def get_context(self):
        context = super().get_context()  # type: ignore
        fieldsets = []

        for title, data in self.Meta.fieldsets:
            fieldset = (title, [])
            for field in data["fields"]:
                bf = self[field]
                errors = self.error_class(bf.errors, renderer=self.renderer)
                fieldset[1].append((bf, errors))

            fieldsets.append(fieldset)

        context["fieldsets"] = fieldsets
        context["numbers"] = False
        return context

    class Meta:
        labels = {
            "nom": "Nom de famille",
            "adresse": "Adresse où vit l'enfant / le jeune",
            "ecole": f"École pour l'année scolaire {Year.get_current().formatted_year}",
            "bapteme": mark_safe("Votre enfant a-t-il reçu <b>le Baptême</b>"),
            "premiere_communion": mark_safe("Votre enfant a-t-il vécu <b>la Première Communion</b>"),
            "profession": mark_safe("Votre enfant a-t-il vécu <b>la Profession de Foi</b>"),
            "confirmation": mark_safe("Votre enfant a-t-il vécu <b>la Confirmation</b>"),
            "adresse_mere": mark_safe("Adresse <small>(si différente de celle où vit l'enfant / le jeune)</small>"),
            "tel_mere": "Téléphone",
            "email_mere": "Email",
            "adresse_pere": mark_safe("Adresse <small>(si différente de celle où vit l'enfant / le jeune)</small>"),
            "tel_pere": "Téléphone",
            "email_pere": "Email",
            "photos": (
                "J'autorise la publication des photos de mon enfant prises au cours "
                "des différentes manifestations liées aux activités du catéchisme / de l'Aumônerie "
                " (plaquettes, presse municipale et locale, site Internet, ...)"
            ),
            "frais": mark_safe(
                "En fonction de leurs possibilités, les familles sont invitées à participer "
                "aux <b>frais du Catéchisme / de l'Aumônerie à partir de 35 euros par enfant</b> "
                "(livres, photocopies, matériel pédagogique, chauffage...).<br>"
                "Participation aux frais, en espèces ou par chèque, à l'ordre de « Aumônerie des Jeunes d'Embrun »"
            ),
        }

        fieldsets = copy.deepcopy(Child.fieldsets)
        del fieldsets[-1]
        # Add authorization document information
        fieldsets[-1][1]["fields"] = (
            fieldsets[-1][1]["fields"][0],
            "autorisation",
            *fieldsets[-1][1]["fields"][1:],
        )

for title, data in SubscriptionForm.Meta.fieldsets:
    for field_name in data["fields"]:
        for field in Child._meta.fields:
            field: models.Field = field
            if field.name == field_name:
                kwargs = {}
                if isinstance(field, models.TextField):
                    kwargs["widget"] = forms.Textarea()
                if isinstance(field, models.DateField):
                    kwargs["widget"] = forms.DateInput(
                        format="%Y-%m-%d",
                        attrs={"type": "date"},
                    )
                if isinstance(field, models.BooleanField):
                    kwargs["form_class"] = BooleanField
                field_obj = field.formfield(**kwargs)
                field_obj.label = SubscriptionForm.Meta.labels.get(field_name, field_obj.label)
                SubscriptionForm.base_fields[field.name] = field_obj


class DateForm(forms.ModelForm):
    class Meta:
        model = Date
        fields = (
            "name",
            "short_name",
            "place",
            "start_date",
            "end_date",
            "start_time",
            "end_time",
            "time_text",
            "cancelled",
            "categories",
        )
        widgets = {
            "categories": CheckboxSelectMultiple,
        }

    def clean_categories(self):
        categories = self.cleaned_data.get("categories")
        if not categories:
            raise forms.ValidationError(_("At least one category must be selected."))
        return categories
