from django.contrib.auth import get_user_model
from django.test import TestCase
from django.urls import reverse

from django_multi_tenant.domains import TenantDomain
from django_multi_tenant.models import Tenant


class TenantDomainAdminTests(TestCase):

    def setUp(self):
        User = get_user_model()

        self.admin_user = User.objects.create_superuser(
            username="admin",
            password="test-password-123"
        )

        self.client.force_login(self.admin_user)

        self.tenant = Tenant.objects.create(
            name="Test Company",
            slug="test-company"
        )

        self.old_domain = TenantDomain.objects.create(
            tenant=self.tenant,
            domain="old.example.com",
            is_primary=True
        )

        self.new_domain = TenantDomain.objects.create(
            tenant=self.tenant,
            domain="new.example.com",
            is_primary=False
        )

    def test_admin_can_change_primary_domain(self):

        url = reverse(
            "admin:django_multi_tenant_tenantdomain_change",
            args=[self.new_domain.pk]
        )

        response = self.client.post(
            url,
            {
                "tenant": self.tenant.pk,
                "domain": "new.example.com",
                "is_primary": "on",
                "_save": "Save",
            }
        )

        self.assertEqual(response.status_code, 302)

        self.old_domain.refresh_from_db()
        self.new_domain.refresh_from_db()

        self.assertFalse(self.old_domain.is_primary)
        self.assertTrue(self.new_domain.is_primary)

    def test_inline_can_change_primary_domain(self):
        url = reverse(
            "admin:django_multi_tenant_tenant_change",
            args=[self.tenant.pk]
        )

        response = self.client.post(
            url,
            {
                # Tenant fields
                "name": "Test Company",
                "slug": "test-company",
                "is_active": "on",

                # Inline management form
                "domains-TOTAL_FORMS": "2",
                "domains-INITIAL_FORMS": "2",
                "domains-MIN_NUM_FORMS": "0",
                "domains-MAX_NUM_FORMS": "1000",

                # Old domain
                "domains-0-id": self.old_domain.pk,
                "domains-0-tenant": self.tenant.pk,
                "domains-0-domain": "old.example.com",

                # New domain
                "domains-1-id": self.new_domain.pk,
                "domains-1-tenant": self.tenant.pk,
                "domains-1-domain": "new.example.com",
                "domains-1-is_primary": "on",

                "_save": "Save",
            }
        )

        self.assertEqual(response.status_code, 302)

        self.old_domain.refresh_from_db()
        self.new_domain.refresh_from_db()

        self.assertFalse(self.old_domain.is_primary)
        self.assertTrue(self.new_domain.is_primary)

    def test_admin_can_move_domain_to_another_tenant(self):
        another_tenant = Tenant.objects.create(
            name="Another Company",
            slug="another-company"
        )

        url = reverse(
            "admin:django_multi_tenant_tenantdomain_change",
            args=[self.new_domain.pk]
        )

        response = self.client.post(
            url,
            {
                "tenant": another_tenant.pk,
                "domain": "new.example.com",
                "is_primary": "on",
                "_save": "Save",
            }
        )

        self.assertEqual(response.status_code, 302)

        self.new_domain.refresh_from_db()

        self.assertEqual(
            self.new_domain.tenant,
            another_tenant
        )

        self.assertTrue(self.new_domain.is_primary)