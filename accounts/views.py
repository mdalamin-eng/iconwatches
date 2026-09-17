from django.contrib.auth import login as auth_login, logout as auth_logout
from django.contrib.auth.views import LoginView
from django.shortcuts import redirect
from .forms import StyledAuthenticationForm


class StaffLoginView(LoginView):
    """Login for admin/manager only. Customers never need an account."""
    template_name = "accounts/login.html"
    authentication_form = StyledAuthenticationForm

    def get_success_url(self):
        return "/dashboard/"


def logout_view(request):
    auth_logout(request)
    return redirect("storefront:home")
