from django import forms
from django.db import models

from .models import Child


class SubscriptionForm(forms.ModelForm):
	class Meta:
		model = Child
		exclude = []
		widgets = {models.DateField: {"widget": forms.widgets.DateInput}}
