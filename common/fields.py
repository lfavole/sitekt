from typing import Any

from django import forms
from django.db import models
from django.utils.safestring import mark_safe


class DatalistField(models.fields.CharField):
    """
    Char field with `<datalist>` in forms.
    """

    def __init__(self, *args, form_choices: tuple[str, ...] = (), **kwargs) -> None:
        self._form_choices = form_choices
        super().__init__(*args, **kwargs)

    def formfield(self, *args, **kwargs):
        return super().formfield(*args, form_class=DatalistFormField, choices=self._form_choices, **kwargs)


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

    def __init__(self, *args, choices=(), **kwargs) -> None:
        choices = [(choice, choice) for choice in choices]
        super().__init__(*args, **kwargs)
        attrs = self.widget.attrs
        attrs |= self.widget_attrs(self.widget)  # type: ignore
        self.widget = DatalistWidget({**self.widget.attrs, **self.widget_attrs(self.widget)}, choices)  # type: ignore

    def valid_value(self, _value):
        return True


class PriceField(models.PositiveIntegerField):
    def formfield(self, *args, **kwargs):
        kwargs["widget"] = PriceInput
        return super().formfield(*args, **kwargs)


class PriceInput(forms.NumberInput):
    """
    Number input with € after it.
    """

    def __init__(self, attrs: dict[str, Any] = {}):
        super().__init__(attrs={"step": 0.1, **attrs})

    def render(self, *args, **kwargs):
        # font-size is for Django administration
        return super().render(*args, **kwargs) + mark_safe('<span style="font-size:1rem;margin-left:0.5em">€</span>')


class DisplayedHTML(forms.Widget):
    def __init__(self, html: str, *args, **kwargs):
        self.html = mark_safe(html)
        super().__init__(*args, **kwargs)

    def render(self, *_args, **_kwargs):
        return self.html


class DisplayedHTMLField(forms.Field):
    def __init__(self, html: str, *args, **kwargs):
        kwargs["widget"] = DisplayedHTML(html)
        super().__init__(*args, label="", label_suffix="", **kwargs)

    def validate(self, _value):
        pass
