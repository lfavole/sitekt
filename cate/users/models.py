from django.contrib.auth.models import AbstractUser
from django.utils.translation import gettext_lazy as _


class User(AbstractUser):
    """
    User model for model swapping.
    It's here if we might need to change the user model and don't unapply the migrations.
    """

    class Meta:
        verbose_name = _("user")
        permissions = [
            ("can_see_debug_toolbar", "Can see debug toolbar"),
        ]
