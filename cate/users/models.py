from django.contrib.auth.models import AbstractUser


class User(AbstractUser):
	"""
	User model for model swapping.
	It's here if we might need to change the user model and don't unapply the migrations.
	"""
