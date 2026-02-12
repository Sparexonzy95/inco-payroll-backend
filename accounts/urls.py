from django.urls import path
from rest_framework_simplejwt.views import TokenObtainPairView, TokenRefreshView

from accounts import views

urlpatterns = [
    path("login/", TokenObtainPairView.as_view()),
    path("refresh/", TokenRefreshView.as_view()),
    path("nonce/", views.wallet_nonce),
    path("wallet-login/", views.wallet_login),
    path("me/", views.me),
    path("set-active-org/", views.set_active_org),
]
