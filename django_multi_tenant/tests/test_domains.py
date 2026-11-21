from django.core.exceptions import ValidationError
from django.db import IntegrityError, transaction
from django.test import TestCase

from django_multi_tenant.domains import TenantDomain
from django_multi_tenant.models import Tenant
from django_multi_tenant.validators import normalize_domain


class TenantDomainValidationTests(TestCase):

    def setUp(self):
        self.tenant = Tenant.objects.create(
            name="Test Company",
            slug="test-company",
        )

    def test_valid_domain(self):
        domain = TenantDomain(
            tenant=self.tenant,
            domain="example.com",
        )

        domain.full_clean()

    def test_invalid_domain(self):
        domain = TenantDomain(
            tenant=self.tenant,
            domain="http://example.com",
        )

        with self.assertRaises(ValidationError):
            domain.full_clean()

    def test_domain_is_normalized_when_saved(self):
        domain = TenantDomain.objects.create(
            tenant=self.tenant,
            domain=" EXAMPLE.COM ",
        )

        self.assertEqual(domain.domain, "example.com")

    def test_domain_normalization_with_update_fields(self):
        domain = TenantDomain.objects.create(
            tenant=self.tenant,
            domain="example.com",
        )

        domain.domain = " NEW-EXAMPLE.COM "

        domain.save(update_fields=["domain"])

        domain.refresh_from_db()

        self.assertEqual(domain.domain, "new-example.com")

    def test_duplicate_domain_with_different_case(self):
        TenantDomain.objects.create(
            tenant=self.tenant,
            domain="example.com",
        )

        another_tenant = Tenant.objects.create(
            name="Another Company",
            slug="another-company",
        )

        with self.assertRaises(IntegrityError):
            TenantDomain.objects.create(
                tenant=another_tenant,
                domain="EXAMPLE.COM",
            )

    def test_valid_international_domain(self):
        domain = TenantDomain(
            tenant=self.tenant,
            domain="مثال.ایران",
        )

        domain.full_clean()

        self.assertEqual(
            domain.domain,
            "xn--mgbh0fb.xn--mgba3a4f16a",
        )

    def test_international_domain_is_saved_as_punycode(self):
        domain = TenantDomain.objects.create(
            tenant=self.tenant,
            domain="مثال.ایران",
        )

        self.assertEqual(
            domain.domain,
            "xn--mgbh0fb.xn--mgba3a4f16a",
        )

    def test_unicode_and_punycode_domains_are_duplicates(self):
        TenantDomain.objects.create(
            tenant=self.tenant,
            domain="مثال.ایران",
        )

        another_tenant = Tenant.objects.create(
            name="Another Company",
            slug="another-company",
        )

        with self.assertRaises(IntegrityError), transaction.atomic():
            TenantDomain.objects.create(
                tenant=another_tenant,
                domain="xn--mgbh0fb.xn--mgba3a4f16a",
            )
    def test_invalid_domain_is_not_saved(self):
        domain = TenantDomain(
            tenant=self.tenant,
            domain="http://example.com",
        )

        with self.assertRaises(ValidationError):
            domain.full_clean()

        self.assertEqual(
            TenantDomain.objects.count(),
            0,
        )

    def test_invalid_domain_cannot_be_saved_directly(self):
        with self.assertRaises(ValidationError):
            TenantDomain.objects.create(
                tenant=self.tenant,
                domain="http://example.com",
            )

        self.assertEqual(
            TenantDomain.objects.count(),
            0,
        )

    def test_none_domain_is_invalid(self):
        with self.assertRaises(ValidationError):
            normalize_domain(None)

    def test_non_string_domain_is_invalid(self):
        with self.assertRaises(ValidationError):
            normalize_domain(123)

    def test_domain_with_multiple_trailing_dots_is_invalid(self):
        with self.assertRaises(ValidationError):
            normalize_domain("example.com..")

    def test_domain_with_three_trailing_dots_is_invalid(self):
        with self.assertRaises(ValidationError):
            normalize_domain("example.com...")