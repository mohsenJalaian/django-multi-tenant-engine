from unittest.mock import patch

from django.db import IntegrityError
from django.test import TestCase

from django_multi_tenant.domains import TenantDomain
from django_multi_tenant.models import Tenant


class TenantModelTests(TestCase):

    def test_tenant_string_representation(self):
        tenant = Tenant.objects.create(
            name="Test Company",
            slug="test-company"
        )

        self.assertEqual(str(tenant), "Test Company")

    def test_slug_must_be_unique(self):
        Tenant.objects.create(
            name="Company One",
            slug="slug"
        )

        with self.assertRaises(IntegrityError):
            Tenant.objects.create(
                name="Company Two",
                slug="slug"
            )
    def test_is_active_defaults_to_true(self):
        tenant = Tenant.objects.create(
            name="Default Company",
            slug="default-company"
        )

        self.assertTrue(tenant.is_active)

    def test_primary_domain_returns_primary_domain(self):
        tenant = Tenant.objects.create(
            name="Test Company",
            slug="test-company"
        )

        TenantDomain.objects.create(
            tenant=tenant,
            domain="company.ir",
            is_primary=False
        )

        TenantDomain.objects.create(
            tenant=tenant,
            domain="company.com",
            is_primary=True
        )

        self.assertEqual(
            tenant.primary_domain.domain,
            "company.com"
        )

    def test_primary_domain_returns_none_when_not_exists(self):
        tenant = Tenant.objects.create(
            name="No Domain Company",
            slug="no-domain-company"
        )

        self.assertIsNone(tenant.primary_domain)

    def test_primary_domain_uses_prefetched_domains(self):
        tenant = Tenant.objects.create(
            name="Test Company",
            slug="test-company"
        )

        TenantDomain.objects.create(
            tenant=tenant,
            domain="company.com",
            is_primary=True
        )

        with self.assertNumQueries(2):
            tenant = Tenant.objects.prefetch_related(
                "domains"
            ).get(pk=tenant.pk)

            primary_domain = tenant.primary_domain

        self.assertEqual(primary_domain.domain, "company.com")

    def test_deactivating_tenant_does_not_delete_domains(self):
        tenant = Tenant.objects.create(
            name="Test Company",
            slug="test-company"
        )

        domain = TenantDomain.objects.create(
            tenant=tenant,
            domain="company.com",
            is_primary=True
        )

        tenant.is_active = False
        tenant.save(update_fields=["is_active"])

        tenant.refresh_from_db()

        self.assertFalse(tenant.is_active)

        self.assertTrue(
            TenantDomain.objects.filter(pk=domain.pk).exists()
        )

    def test_inactive_tenant_still_has_primary_domain(self):
        tenant = Tenant.objects.create(
            name="Test Company",
            slug="test-company",
            is_active=False
        )

        domain = TenantDomain.objects.create(
            tenant=tenant,
            domain="company.com",
            is_primary=True
        )

        self.assertEqual(
            tenant.primary_domain,
            domain
        )

    def test_set_as_primary_does_not_affect_other_tenants(self):
        tenant1 = Tenant.objects.create(
            name="Company One",
            slug="company-one"
        )

        tenant2 = Tenant.objects.create(
            name="Company Two",
            slug="company-two"
        )

        domain1 = TenantDomain.objects.create(
            tenant=tenant1,
            domain="one.example.com",
            is_primary=True
        )

        domain2 = TenantDomain.objects.create(
            tenant=tenant2,
            domain="two.example.com",
            is_primary=True
        )

        domain2.set_as_primary()

        domain1.refresh_from_db()
        domain2.refresh_from_db()

        self.assertTrue(domain1.is_primary)
        self.assertTrue(domain2.is_primary)

class TenantDomainTests(TestCase):

    def test_domain_belongs_to_tenant(self):
        tenant = Tenant.objects.create(
            name="Test Company",
            slug="test-company"
        )

        domain = TenantDomain.objects.create(
            tenant=tenant,
            domain="test-company.example.com",
            is_primary=True
        )

        self.assertEqual(domain.tenant, tenant)
    def test_domain_must_be_unique(self):
        tenant1 = Tenant.objects.create(
            name="Company One",
            slug="company-one"
        )

        tenant2 = Tenant.objects.create(
            name="Company Two",
            slug="company-two"
        )

        TenantDomain.objects.create(
            tenant=tenant1,
            domain="shared.example.com"
        )

        with self.assertRaises(IntegrityError):
            TenantDomain.objects.create(
                tenant=tenant2,
                domain="shared.example.com"
            )

    def test_tenant_cannot_have_two_primary_domains(self):
        tenant = Tenant.objects.create(
            name="Test Company",
            slug="test-company"
        )

        TenantDomain.objects.create(
            tenant=tenant,
            domain="company.com",
            is_primary=True
        )

        with self.assertRaises(IntegrityError):
            TenantDomain.objects.create(
                tenant=tenant,
                domain="company.ir",
                is_primary=True
            )

    def test_tenant_can_have_multiple_secondary_domains(self):
        tenant = Tenant.objects.create(
            name="Test Company",
            slug="test-company"
        )

        TenantDomain.objects.create(
            tenant=tenant,
            domain="company.ir",
            is_primary=False
        )

        TenantDomain.objects.create(
            tenant=tenant,
            domain="company.net",
            is_primary=False
        )

        self.assertEqual(tenant.domains.count(), 2)

    def test_set_as_primary_changes_primary_domain(self):
        tenant = Tenant.objects.create(
            name="Test Company",
            slug="test-company"
        )

        old_domain = TenantDomain.objects.create(
            tenant=tenant,
            domain="company.com",
            is_primary=True
        )

        new_domain = TenantDomain.objects.create(
            tenant=tenant,
            domain="company.ir",
            is_primary=False
        )

        new_domain.set_as_primary()

        old_domain.refresh_from_db()
        new_domain.refresh_from_db()

        self.assertFalse(old_domain.is_primary)
        self.assertTrue(new_domain.is_primary)

    def test_set_as_primary_rolls_back_on_error(self):
        tenant = Tenant.objects.create(
            name="Test Company",
            slug="test-company"
        )

        old_domain = TenantDomain.objects.create(
            tenant=tenant,
            domain="company.com",
            is_primary=True
        )

        new_domain = TenantDomain.objects.create(
            tenant=tenant,
            domain="company.ir",
            is_primary=False
        )

        with (
            patch.object(
                TenantDomain,
                "save",
                side_effect=RuntimeError("Simulated error"),
            ),
            self.assertRaises(RuntimeError),
        ):
            new_domain.set_as_primary()

        old_domain.refresh_from_db()
        new_domain.refresh_from_db()

        self.assertTrue(old_domain.is_primary)
        self.assertFalse(new_domain.is_primary)

    def test_set_as_primary_is_idempotent(self):
        tenant = Tenant.objects.create(
            name="Test Company",
            slug="test-company"
        )

        primary_domain = TenantDomain.objects.create(
            tenant=tenant,
            domain="company.com",
            is_primary=True
        )

        secondary_domain = TenantDomain.objects.create(
            tenant=tenant,
            domain="company.ir",
            is_primary=False
        )

        primary_domain.set_as_primary()

        primary_domain.refresh_from_db()
        secondary_domain.refresh_from_db()

        self.assertTrue(primary_domain.is_primary)
        self.assertFalse(secondary_domain.is_primary)

    def test_set_as_primary_does_not_affect_other_tenants(self):
        tenant_a = Tenant.objects.create(
            name="Company A",
            slug="company-a"
        )

        tenant_b = Tenant.objects.create(
            name="Company B",
            slug="company-b"
        )

        a_old = TenantDomain.objects.create(
            tenant=tenant_a,
            domain="a.com",
            is_primary=True
        )

        a_new = TenantDomain.objects.create(
            tenant=tenant_a,
            domain="a.ir",
            is_primary=False
        )

        b_primary = TenantDomain.objects.create(
            tenant=tenant_b,
            domain="b.com",
            is_primary=True
        )

        b_secondary = TenantDomain.objects.create(
            tenant=tenant_b,
            domain="b.ir",
            is_primary=False
        )

        a_new.set_as_primary()

        a_old.refresh_from_db()
        a_new.refresh_from_db()
        b_primary.refresh_from_db()
        b_secondary.refresh_from_db()

        self.assertFalse(a_old.is_primary)
        self.assertTrue(a_new.is_primary)

        self.assertTrue(b_primary.is_primary)
        self.assertFalse(b_secondary.is_primary)

    def test_set_as_primary_fails_for_unsaved_domain(self):
        tenant = Tenant.objects.create(
            name="Test Company",
            slug="test-company"
        )

        domain = TenantDomain(
            tenant=tenant,
            domain="new.example.com"
        )

        with self.assertRaises(TenantDomain.DoesNotExist):
            domain.set_as_primary()

    def test_set_as_primary_rejects_wrong_tenant(self):
        tenant1 = Tenant.objects.create(
            name="Company One",
            slug="company-one"
        )

        tenant2 = Tenant.objects.create(
            name="Company Two",
            slug="company-two"
        )

        domain = TenantDomain.objects.create(
            tenant=tenant1,
            domain="company-one.com",
            is_primary=False
        )

        domain.tenant_id = tenant2.pk

        with self.assertRaises(TenantDomain.DoesNotExist):
            domain.set_as_primary()

        domain.refresh_from_db()

        self.assertEqual(domain.tenant_id, tenant1.pk)
        self.assertFalse(domain.is_primary)

    def test_deleting_tenant_deletes_its_domains(self):
        tenant = Tenant.objects.create(
            name="Test Company",
            slug="test-company"
        )

        domain = TenantDomain.objects.create(
            tenant=tenant,
            domain="company.example.com",
            is_primary=True
        )

        tenant.delete()

        self.assertFalse(
            TenantDomain.objects.filter(pk=domain.pk).exists()
        )

    def test_deleting_domain_does_not_delete_tenant(self):
        tenant = Tenant.objects.create(
            name="Test Company",
            slug="test-company"
        )

        domain1 = TenantDomain.objects.create(
            tenant=tenant,
            domain="company.com",
            is_primary=True
        )

        domain2 = TenantDomain.objects.create(
            tenant=tenant,
            domain="company.ir",
            is_primary=False
        )

        domain1.delete()

        self.assertTrue(
            Tenant.objects.filter(pk=tenant.pk).exists()
        )

        self.assertTrue(
            TenantDomain.objects.filter(pk=domain2.pk).exists()
        )

    def test_set_as_primary_does_not_change_domain_owner(self):
        tenant1 = Tenant.objects.create(
            name="Company One",
            slug="company-one"
        )

        tenant2 = Tenant.objects.create(
            name="Company Two",
            slug="company-two"
        )

        domain = TenantDomain.objects.create(
            tenant=tenant1,
            domain="one.example.com",
            is_primary=True
        )

        original_tenant_id = domain.tenant_id

        domain.set_as_primary()

        domain.refresh_from_db()

        self.assertEqual(domain.tenant_id, original_tenant_id)
        self.assertEqual(domain.tenant_id, tenant1.id)
        self.assertNotEqual(domain.tenant_id, tenant2.id)

    def test_domain_is_normalized_with_update_fields(self):
        tenant = Tenant.objects.create(
            name="Test Company",
            slug="test-company"
        )

        domain = TenantDomain.objects.create(
            tenant=tenant,
            domain="company.com"
        )

        domain.domain = " EXAMPLE.COM "
        domain.save(update_fields=["is_primary"])

        domain.refresh_from_db()

        self.assertEqual(domain.domain, "example.com")
