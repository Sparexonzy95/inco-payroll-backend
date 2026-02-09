from django.urls import path
from . import views

urlpatterns = [
    path("tx/submit/", views.submit_tx),
    path("tx/", views.list_txs),
]
