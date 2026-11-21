from django.test import TestCase

from django_multi_tenant.domains import TenantDomain
from django_multi_tenant.models import Tenant


class TenantViewTests(TestCase):

    def setUp(self):
        self.tenant = Tenant.objects.create(
            name="Test Company",
            slug="test-company"
        )

        TenantDomain.objects.create(
            tenant=self.tenant,
            domain="test-company.example.com",
            is_primary=True
        )

    def test_current_tenant_returns_tenant_data(self):
        response = self.client.get(
            "/tenant/",
            HTTP_HOST="test-company.example.com"
        )

        self.assertEqual(response.status_code, 200)

        self.assertEqual(
            response.json()["tenant_name"],
            "Test Company"
        )

        self.assertEqual(
            response.json()["tenant_slug"],
            "test-company"
        )

    def test_current_tenant_returns_404_for_unknown_domain(self):
        response = self.client.get(
            "/tenant/",
            HTTP_HOST="unknown.example.com"
        )

        self.assertEqual(response.status_code, 404)