from django import forms

from .models import Child

class SubscriptionForm(forms.ModelForm):
	class Meta:
		model = Child
		exclude = []
