from django.urls import path
from orgs import views

urlpatterns = [
    path("", views.list_my_orgs),
]
