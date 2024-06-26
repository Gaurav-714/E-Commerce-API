from django.urls import path
from .views import *

urlpatterns = [
    path('account/register', RegisterUserView.as_view()),
    path('account/login', LoginUserView.as_view()),
    path('account/update', UpdateUserView.as_view()),
    path('account/forgot_password', ForgotPasswordView.as_view()),
    path('account/reset_password/<str:token>', ResetPasswordView.as_view()),
]
