from allauth.account.models import EmailAddress
from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as DjangoUserAdmin

from .models import User


class EmailAddressInline(admin.TabularInline):
    model = EmailAddress
    extra = 0


@admin.register(User)
class UserAdmin(DjangoUserAdmin):
    inlines = [EmailAddressInline]
