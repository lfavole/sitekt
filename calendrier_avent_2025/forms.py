import datetime as dt

from django import forms
from django.conf import settings
from django.utils.formats import ISO_INPUT_FORMATS


class SetDateForm(forms.Form):
    new_date = forms.DateField(
        label="Nouvelle date",
        widget=forms.widgets.DateInput({"type": "date"}, ISO_INPUT_FORMATS["DATE_INPUT_FORMATS"][0]),
        initial=lambda: dt.date.today(),
        # ISO formats must be first so the first format is the one accepted by <input type="date">
        input_formats=ISO_INPUT_FORMATS["DATE_INPUT_FORMATS"] + settings.DATE_INPUT_FORMATS,
    )
