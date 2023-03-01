from django.views.generic import CreateView
from django.contrib.auth.views import PasswordResetView
from django.urls import reverse_lazy
from .forms import (
    CreationForm,
    PassResetForm,
)
from .const import (
    PASSWORD_RESET_TEMPLATE,
    SIGNUP_TEMPLATE,
)


class SignUp(CreateView):
    form_class = CreationForm
    success_url = reverse_lazy('posts:main')
    template_name = SIGNUP_TEMPLATE


class PassResetView(PasswordResetView):
    form_class = PassResetForm
    template_name = PASSWORD_RESET_TEMPLATE
    # In basic Django's PasswordResetView when email has mistake
    # or doesn't exsist no email will be sent, but the user won’t
    # receive any error message either.
    # This prevents information leaking to potential attackers.
    # If you want to provide an error message in this case,
    # you can subclass PasswordResetForm and use the form_class attribute.
