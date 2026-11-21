
from django.test import TestCase

from django_multi_tenant.models import Tenant


class TenantQuerySetTest(TestCase):
    def setUp(self):
        self.active_tenant = Tenant.objects.create(
            name="Active Company",
            slug="active-company",
            is_active=True
        )
        self.inactive_tenant = Tenant.objects.create(
            name="Inactive Company",
            slug="inactive-company",
            is_active=False
        )
    def test_active_returns_only_active_tenant(self):
        result=list(Tenant.objects.active())
        self.assertEqual(result,[self.active_tenant])

    def test_inactive_returns_only_inactive_tenants(self):
        result = list(Tenant.objects.inactive())

        self.assertEqual(result, [self.inactive_tenant])

    def test_by_slug_returns_correct_tenant(self):
        result = Tenant.objects.by_slug("active-company").first()

        self.assertEqual(result, self.active_tenant)