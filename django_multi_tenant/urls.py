from django.urls import path

from .views import current_tenant

urlpatterns = [
    path("tenant/", current_tenant, name="current_tenant"),
]