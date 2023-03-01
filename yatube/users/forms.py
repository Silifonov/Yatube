from django.contrib.auth.forms import (
    UserCreationForm,
    PasswordResetForm,
)
from django.forms import ValidationError
from django.contrib.auth import get_user_model


User = get_user_model()

ERROR_MESSAGE_EMAIL_REPEATS = 'Пользователь с таким email уже зарегистрирован'
ERROR_MESSAGE_EMAIL_DOESNT_EXSIST = (
    'Пользователь с таким email не зарегистрирован')


class CreationForm(UserCreationForm):
    class Meta(UserCreationForm.Meta):
        model = User
        fields = ('first_name', 'last_name', 'username', 'email')

    def clean_email(self):
        """Проверяет есть ли уже в БД пользователь с таким же email."""
        email = self.cleaned_data['email']
        if email is not None:
            if User.objects.filter(email__exact=email).first():
                raise ValidationError(ERROR_MESSAGE_EMAIL_REPEATS)
            return email


class PassResetForm(PasswordResetForm):

    def clean_email(self):
        """Проверяет существует ли пользователь с введенным email"""
        email = self.cleaned_data['email']
        if User.objects.filter(email__exact=email).first() is None:
            raise ValidationError(ERROR_MESSAGE_EMAIL_DOESNT_EXSIST)
        return email
