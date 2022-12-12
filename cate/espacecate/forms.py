from django import forms

from .models import Enfant

class SubscriptionForm(forms.ModelForm):
	class Meta:
		model = Enfant
		exclude = []
