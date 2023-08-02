import copy
from typing import Any, Literal, Type

from betterforms.forms import BetterModelForm
from django import forms
from django.db import models
from django.utils.safestring import SafeString


class DatalistWidget(forms.widgets.Select):
    """
    Widget for `<datalist>`.
    """
    template_name = "widgets/datalist.html"

class DatalistFormField(forms.ChoiceField, forms.CharField):
    """
    Text field with `<datalist>`.
    """
    widget = DatalistWidget
    def __init__(self, *args, choices = (), **kwargs) -> None:
        choices = [(choice, choice) for choice in choices]
        super().__init__(*args, **kwargs)
        attrs = self.widget.attrs
        attrs |= self.widget_attrs(self.widget) # type: ignore
        self.widget = DatalistWidget({**self.widget.attrs, **self.widget_attrs(self.widget)}, choices) # type: ignore

    def valid_value(self, _value):
        return True

class PriceInput(forms.NumberInput):
    """
    Number input with € after it.
    """
    def __init__(self, attrs: dict[str, Any] = {}):
        super().__init__(attrs = {"step": 0.1, **attrs})

    def render(self, *args, **kwargs):
        # font-size is for Django administration
        return super().render(*args, **kwargs) + '<span style="font-size:1rem;margin-left:0.5em">€</span>'

class DisplayedHTML(forms.Widget):
    def __init__(self, html: str, *args, **kwargs):
        self.html = SafeString(html)
        super().__init__(*args, **kwargs)

    def render(self, *_args, **_kwargs):
        return self.html

class DisplayedHTMLField(forms.Field):
    def __init__(self, html: str, *args, **kwargs):
        kwargs["widget"] = DisplayedHTML(html)
        super().__init__(*args, label="", label_suffix="", **kwargs)

    def validate(self, _value):
        pass


def get_subscription_form(app: Literal["espacecate", "aumonerie"], target_model: Type[models.Model]):
    """
    Return the subscription form for the given `Child` model.
    """
    from .models import Year  # avoid circular import

    def formfield_for_dbfield(db_field, **kwargs):
        if isinstance(db_field, models.DateField):
            kwargs["widget"] = forms.DateInput(
                format="%Y-%m-%d",
                attrs={"type": "date"},
            )
        if isinstance(db_field, models.BooleanField):
            kwargs["widget"] = forms.RadioSelect(
                choices=[(True, "Oui"), (False, "Non")],
            )
        return db_field.formfield(**kwargs)

    class SubscriptionForm(BetterModelForm):  # pylint: disable=W0223
        autorisation = DisplayedHTMLField(
            "Un document intitulé <b>« Autorisation et engagement »</b> devra être signé par vos soins.<br>"
            'Vous pouvez <a class="autorisation" href="#">le télécharger</a>, '
            "l'imprimer, le compléter, le signer et nous le rapporter à la prochaine rencontre du catéchisme, "
            "sinon une version papier vous sera donnée."
        )

        class Meta:
            model = target_model
            labels = {
                "nom": "Nom de famille",
                "adresse": "Adresse des parents",
                "ecole": f"École pour l'année scolaire {Year.get_current().formatted_year}",
                "bapteme": SafeString("Votre enfant a-t-il reçu <b>le Baptême</b>"),
                "pardon": SafeString("Votre enfant a-t-il vécu <b>le Sacrement du Pardon</b>"),
                "premiere_communion": SafeString("Votre enfant a-t-il vécu <b>la Première Communion</b>"),
                "profession": SafeString("Votre enfant a-t-il vécu <b>la Profession de Foi</b>"),
                "confirmation": SafeString("Votre enfant a-t-il vécu <b>la Confirmation</b>"),
                "adresse_mere": SafeString("Adresse <small>(si différente de celle des parents)</small>"),
                "tel_mere": "Téléphone",
                "email_mere": "Email",
                "adresse_pere": SafeString("Adresse <small>(si différente de celle des parents)</small>"),
                "tel_pere": "Téléphone",
                "email_pere": "Email",
                "freres_soeurs": "Frères et sœurs (prénoms et âges)",
                "infos": (
                    "Autres informations à nous communiquer "
                    "(histoire de l'enfant, problèmes de santé, difficultés rencontrées, ...)"
                ),
                "photos": (
                    "J'autorise la publication des photos de mon enfant prises au cours "
                    + "des différentes manifestations liées aux activités "
                    + {"espacecate": "du catéchisme", "aumonerie": "de l'Aumônerie"}[app]
                    + " (plaquettes, presse municipale et locale, site Internet, ...)"
                ),
                "frais": SafeString(
                    "En fonction de leurs possibilités, les familles sont invitées à participer "
                    "aux <b>frais du Catéchisme à partir de 35 euros par enfant</b> "
                    "(livres, photocopies, matériel pédagogique, chauffage...).<br>"
                    "Participation aux frais, en espèces ou par chèque, à l'ordre de « Paroisses de l'Embrunais »"
                ) if app == "espacecate" else (
                    f"Participation aux frais (cotisation pour l'année {Year.get_current().formatted_year} : "
                    "à partir de 20 euros à l'ordre de « Aumônerie des Jeunes d'Embrun », en espèces ou par chèque)"
                )
            }
            exclude = ["paye", "signe", "groupe", "photo"]
            formfield_callback = formfield_for_dbfield
            fieldsets = copy.deepcopy(target_model.fieldsets)  # type: ignore
            fieldsets.pop()  # remove admin section
            # add authorization document information
            fieldsets[-1][1]["fields"] = (fieldsets[-1][1]["fields"][0], "autorisation", *fieldsets[-1][1]["fields"][1:])

    return SubscriptionForm
