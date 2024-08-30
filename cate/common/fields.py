from django.db import models

from .forms import DatalistFormField, PriceInput


class DatalistField(models.fields.CharField):
    """
    Char field with `<datalist>` in forms.
    """

    def __init__(self, *args, form_choices: tuple[str, ...] = (), **kwargs) -> None:
        self._form_choices = form_choices
        super().__init__(*args, **kwargs)

    def formfield(self, *args, **kwargs):
        return super().formfield(*args, form_class=DatalistFormField, choices=self._form_choices, **kwargs)


class PriceField(models.PositiveIntegerField):
    def formfield(self, *args, **kwargs):
        kwargs["widget"] = PriceInput
        return super().formfield(*args, **kwargs)
