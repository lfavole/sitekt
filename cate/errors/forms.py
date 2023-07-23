from django import forms
from django.utils.translation import gettext_lazy as _


class ErrorForm(forms.Form):
    """
    Form to quickly go to an error.
    """

    id = forms.IntegerField(min_value=1, required=True, label=_("error ID"))
