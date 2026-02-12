from django.contrib import admin
from django.urls import path, include

urlpatterns = [
    path("admin/", admin.site.urls),
    path("api/auth/", include("accounts.urls")),
    path("api/payroll/", include("payroll.urls")),
    #path("api/chain/", include("chain.urls")),
]
