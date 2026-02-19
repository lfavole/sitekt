from html import escape

from allauth.account.models import EmailAddress
from allauth.core.internal import ratelimit
from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as DjangoUserAdmin
from django.http import HttpResponseRedirect
from django.http.request import HttpRequest
from django.urls import path, reverse
from django.utils.html import mark_safe

from .models import User, Webhook


class EmailAddressInline(admin.TabularInline):
    model = EmailAddress
    extra = 0


@admin.register(Webhook)
class WebhookAdmin(admin.ModelAdmin):
    raw_id_fields = ("user",)

    def get_urls(self):
        return [
            path(
                "<path:object_id>/send_test_payload/",
                self.admin_site.admin_view(self.send_test_payload),
                name=f"{self.opts.app_label}_{self.opts.model_name}_send_test_payload",
            ),
        ] + super().get_urls()

    def send_test_payload(self, request, object_id):
        # rate limit?
        return Webhook.objects.get(pk=object_id).send_request({"child_name": "Test Test"})


class WebhookInline(admin.TabularInline):
    model = Webhook
    extra = 0
    fields = ["link"]
    readonly_fields = ["link"]

    def link(self, obj):
        url = reverse(
            "admin:%s_%s_change" % (self.opts.app_label, self.opts.model_name),
            args=(obj.pk,),
            current_app=self.admin_site.name,
        )
        return mark_safe(f'<a href="{escape(url)}" target="_blank">{escape(str(obj))}</a>')

    def has_add_permission(self, *args, **kwargs):
        return False


@admin.register(User)
class UserAdmin(DjangoUserAdmin):
    inlines = [EmailAddressInline, WebhookInline]
