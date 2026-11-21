from django.apps import AppConfig


class DjangoMultiTenantConfig(AppConfig):
    default_auto_field = "django.db.models.BigAutoField"
    name = "django_multi_tenant"
