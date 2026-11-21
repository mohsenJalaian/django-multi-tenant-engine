from django.test import TestCase

from django_multi_tenant.domains import TenantDomain
from django_multi_tenant.models import Tenant
from django_multi_tenant.resolver import get_tenant_from_domain


class TenantResolverTests(TestCase):

    def test_resolver_returns_none_for_inactive_tenant(self):
        tenant = Tenant.objects.create(
            name="Inactive Company",
            slug="inactive-company",
            is_active=False
        )

        TenantDomain.objects.create(
            tenant=tenant,
            domain="inactive.example.com",
            is_primary=True
        )

        result = get_tenant_from_domain("inactive.example.com")

        self.assertIsNone(result)

    def test_resolver_returns_active_tenant(self):
        tenant = Tenant.objects.create(
            name="Active Company",
            slug="active-company"
        )

        TenantDomain.objects.create(
            tenant=tenant,
            domain="active.example.com",
            is_primary=True
        )

        result = get_tenant_from_domain("active.example.com")

        self.assertEqual(result, tenant)

    def test_resolver_returns_none_for_unknown_domain(self):
        result = get_tenant_from_domain("unknown.example.com")

        self.assertIsNone(result)

    def test_resolver_supports_international_domain(self):
        tenant = Tenant.objects.create(
            name="Persian Company",
            slug="persian-company"
        )

        TenantDomain.objects.create(
            tenant=tenant,
            domain="مثال.ایران",
            is_primary=True
        )

        result = get_tenant_from_domain("مثال.ایران")

        self.assertEqual(result, tenant)

    def test_resolver_normalizes_domain(self):
        tenant = Tenant.objects.create(
            name="Normalization Company",
            slug="normalization-company"
        )

        TenantDomain.objects.create(
            tenant=tenant,
            domain="normalization.example.com",
            is_primary=True
        )

        result = get_tenant_from_domain(
            "  NORMALIZATION.EXAMPLE.COM  "
        )

        self.assertEqual(result, tenant)

    def test_resolver_returns_none_for_invalid_domain(self):
        result = get_tenant_from_domain("invalid domain!")

        self.assertIsNone(result)

    def test_resolver_supports_trailing_dot(self):
        tenant = Tenant.objects.create(
            name="Trailing Dot Company",
            slug="trailing-dot-company"
        )

        TenantDomain.objects.create(
            tenant=tenant,
            domain="trailing.example.com",
            is_primary=True
        )

        result = get_tenant_from_domain(
            "trailing.example.com."
        )

        self.assertEqual(result, tenant)

    def test_resolver_returns_none_for_empty_domain(self):
        result = get_tenant_from_domain("")

        self.assertIsNone(result)

    def test_resolver_returns_none_for_whitespace_domain(self):
        result = get_tenant_from_domain("   ")

        self.assertIsNone(result)

    def test_resolver_returns_none_for_none_domain(self):
        result = get_tenant_from_domain(None)

        self.assertIsNone(result)

    def test_resolver_returns_none_for_non_string_domain(self):
        result = get_tenant_from_domain(12345)

        self.assertIsNone(result)

    def test_inactive_tenant_domain_returns_none(self):
        tenant = Tenant.objects.create(
            name="Inactive Company",
            slug="inactive-company",
            is_active=False
        )

        TenantDomain.objects.create(
            tenant=tenant,
            domain="inactive.example.com",
            is_primary=True
        )

        result = get_tenant_from_domain("inactive.example.com")

        self.assertIsNone(result)

    def test_resolver_does_not_return_tenant_after_deactivation(self):
        tenant = Tenant.objects.create(
            name="Test Company",
            slug="test-company",
            is_active=True
        )

        TenantDomain.objects.create(
            tenant=tenant,
            domain="company.example.com",
            is_primary=True
        )

        result_before = get_tenant_from_domain(
            "company.example.com"
        )

        self.assertEqual(result_before, tenant)

        tenant.is_active = False
        tenant.save(update_fields=["is_active"])

        result_after = get_tenant_from_domain(
            "company.example.com"
        )

        self.assertIsNone(result_after)

    def test_resolver_returns_tenant_after_reactivation(self):
        tenant = Tenant.objects.create(
            name="Test Company",
            slug="test-company",
            is_active=False
        )

        TenantDomain.objects.create(
            tenant=tenant,
            domain="company.example.com",
            is_primary=True
        )

        result_before = get_tenant_from_domain(
            "company.example.com"
        )

        self.assertIsNone(result_before)

        tenant.is_active = True
        tenant.save(update_fields=["is_active"])

        result_after = get_tenant_from_domain(
            "company.example.com"
        )

        self.assertEqual(result_after, tenant)

    def test_resolver_normalizes_idna_domain(self):
        tenant = Tenant.objects.create(
            name="IDNA Company",
            slug="idna-company"
        )

        TenantDomain.objects.create(
            tenant=tenant,
            domain="fass.example.com",
            is_primary=True
        )

        result = get_tenant_from_domain("faß.example.com")

        self.assertEqual(result, tenant)