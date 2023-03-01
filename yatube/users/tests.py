from http import HTTPStatus
from django.urls import reverse
from django.contrib.auth import get_user_model
from django.test import (
    TestCase,
    Client
)
from .const import (
    SIGNUP_URL_NAME,
    PASSWORD_RESET_URL_NAME,
)
from .forms import (
    ERROR_MESSAGE_EMAIL_REPEATS,
    ERROR_MESSAGE_EMAIL_DOESNT_EXSIST,
)

User = get_user_model()


class FormValidationTests(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.email = 'user@testmail.com'
        cls.user = User.objects.create_user(
            username='test_user',
            email=cls.email
        )

    def test_signup_form_email_validation(self):
        registred_users_count = User.objects.count()
        password = 'l7dccBopg'
        form_data = {
            'username': 'test_client',
            'email': self.email,
            'password1': password,
            'password2': password,
        }
        response = Client().post(
            reverse(SIGNUP_URL_NAME),
            data=form_data,
            follow=True
        )
        self.assertEqual(User.objects.count(), registred_users_count)
        self.assertFormError(
            response,
            'form',
            'email',
            ERROR_MESSAGE_EMAIL_REPEATS
        )
        self.assertEqual(response.status_code, HTTPStatus.OK)

    def test_password_reset_form_email_validation(self):
        form_data = {
            'email': 'user@test.com',
        }
        response = Client().post(
            reverse(PASSWORD_RESET_URL_NAME),
            data=form_data,
            follow=True
        )
        self.assertFormError(
            response,
            'form',
            'email',
            ERROR_MESSAGE_EMAIL_DOESNT_EXSIST
        )
        self.assertEqual(response.status_code, HTTPStatus.OK)
