from django.urls import path
from rest_framework_simplejwt.views import TokenRefreshView

from accounts import views

urlpatterns = [
    path("refresh/", TokenRefreshView.as_view()),
    path("nonce/", views.wallet_nonce),
    path("wallet-login/", views.wallet_login),
    path("me/", views.me),
    path("employer/register/", views.employer_register),
]
