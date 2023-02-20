from django.urls import path
from django.contrib.auth.views import (
    LogoutView,
    LoginView,
    PasswordResetView,
    PasswordResetDoneView,
    PasswordResetConfirmView,
    PasswordResetCompleteView,
    PasswordChangeView,
    PasswordChangeDoneView,
)
from . import views
from .const import (
    LOGGED_OUT_TEMPLATE,
    LOGIN_TEMPLATE,
    PASSWORD_RESET_TEMPLATE,
    PASSWORD_RESET_DONE_TEMPLATE,
    PASSWORD_RESET_CONFIRM_TEMPLATE,
    PASSWORD_RESET_COMPLETE_TEMPLATE,
    PASSWORD_CHANGE_TEMPLATE,
    PASSWORD_CHANGE_DONE_TEMPLATE,
)


app_name = 'users'


urlpatterns = [
    path('signup/', views.SignUp.as_view(), name='signup'),
    path(
        'logout/',
        LogoutView.as_view(template_name=LOGGED_OUT_TEMPLATE),
        name='logout'
    ),
    path(
        'login/',
        LoginView.as_view(template_name=LOGIN_TEMPLATE),
        name='login'
    ),
    path(
        'password_reset/',
        PasswordResetView.as_view(template_name=PASSWORD_RESET_TEMPLATE),
        name='password_reset'
    ),
    path(
        'password_reset/done/',
        PasswordResetDoneView.as_view(
            template_name=PASSWORD_RESET_DONE_TEMPLATE),
        name='password_reset_done'
    ),
    path(
        'reset/<uidb64>/<token>/',
        PasswordResetConfirmView.as_view(
            template_name=PASSWORD_RESET_CONFIRM_TEMPLATE),
        name='password_reset_confirm'
    ),
    path(
        'reset/done/',
        PasswordResetCompleteView.as_view(
            template_name=PASSWORD_RESET_COMPLETE_TEMPLATE),
        name='password_reset_complete'
    ),
    path(
        'password_change/',
        PasswordChangeView.as_view(template_name=PASSWORD_CHANGE_TEMPLATE),
        name='password_change'
    ),
    path(
        'password_change/done/',
        PasswordChangeDoneView.as_view(
            template_name=PASSWORD_CHANGE_DONE_TEMPLATE),
        name='password_change_done'
    ),
]
