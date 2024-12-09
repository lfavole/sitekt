from allauth.account import views
from allauth.account.adapter import DefaultAccountAdapter
from allauth.socialaccount.adapter import DefaultSocialAccountAdapter, get_adapter
from allauth.socialaccount.models import SocialApp
from django.shortcuts import resolve_url


class Adapter(DefaultAccountAdapter):
    """Dummy adapter."""


def patch(old):
    """Add parameters for One Tap sign-in."""
    def get_context_data(self, **kwargs):
        ret = old(self, **kwargs)

        # pass settings to the template for One Tap sign-in
        try:
            adapter: DefaultSocialAccountAdapter = get_adapter()
            app: SocialApp = adapter.get_app(self.request, "google")
            ret["GOOGLE_CLIENT_ID"] = app.client_id
        except SocialApp.DoesNotExist:
            pass

        ret["GOOGLE_REDIRECT_URI"] = self.request.build_absolute_uri(resolve_url("google_callback"))

        return ret

    return get_context_data


views.LoginView.get_context_data = patch(views.LoginView.get_context_data)
views.SignupView.get_context_data = patch(views.SignupView.get_context_data)
