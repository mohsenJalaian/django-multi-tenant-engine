from django.core.exceptions import DisallowedHost
from django.http import HttpResponse
from django.test import RequestFactory, TestCase, override_settings

from django_multi_tenant.domains import TenantDomain
from django_multi_tenant.middleware import TenantMiddleware
from django_multi_tenant.models import Tenant


class TenantMiddlewareTests(TestCase):

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

        self.factory = RequestFactory()

        self.middleware = TenantMiddleware(
            lambda request: None
        )

    def test_middleware_resolves_tenant(self):
        request = self.factory.get(
            "/products/",
            HTTP_HOST="test-company.example.com"
        )

        self.middleware(request)

        self.assertEqual(request.tenant, self.tenant)

    def test_middleware_returns_none_for_unknown_domain(self):
        request = self.factory.get(
            "/products/",
            HTTP_HOST="unknown.example.com"
        )

        self.middleware(request)

        self.assertIsNone(request.tenant)

    @override_settings(
        ALLOWED_HOSTS=["xn--mgbh0fb.xn--mgba3a4f16a"]
    )
    def test_middleware_resolves_international_domain(self):
        tenant = Tenant.objects.create(
            name="Persian Company",
            slug="persian-company"
        )

        TenantDomain.objects.create(
            tenant=tenant,
            domain="مثال.ایران",
            is_primary=True
        )

        request = self.factory.get(
            "/products/",
            HTTP_HOST="xn--mgbh0fb.xn--mgba3a4f16a"
        )

        self.middleware(request)

        self.assertEqual(request.tenant, tenant)

    def test_middleware_returns_response(self):
        expected_response = "Hello from view"

        middleware = TenantMiddleware(
            lambda request: expected_response
        )

        request = self.factory.get(
            "/products/",
            HTTP_HOST="test-company.example.com"
        )

        response = middleware(request)

        self.assertEqual(response, expected_response)

    def test_middleware_resolves_tenant_with_port(self):
        request = self.factory.get(
            "/products/",
            HTTP_HOST="test-company.example.com:8000"
        )

        self.middleware(request)

        self.assertEqual(request.tenant, self.tenant)

    @override_settings(ALLOWED_HOSTS=["test-company.example.com"])
    def test_middleware_rejects_disallowed_host(self):
        request = self.factory.get(
            "/",
            HTTP_HOST="malicious.example"
        )

        with self.assertRaises(DisallowedHost):
            self.middleware(request)

    @override_settings(ALLOWED_HOSTS=["inactive.example.com"])
    def test_inactive_tenant_sets_request_tenant_to_none(self):
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

        request = self.factory.get(
            "/",
            HTTP_HOST="inactive.example.com"
        )

        middleware = TenantMiddleware(
            lambda request: HttpResponse("OK")
        )

        middleware(request)

        self.assertIsNone(request.tenant)

    @override_settings(ALLOWED_HOSTS=["reactivated.example.com"])
    def test_middleware_resolves_reactivated_tenant(self):
        tenant = Tenant.objects.create(
            name="Reactivated Company",
            slug="reactivated-company",
            is_active=False
        )

        TenantDomain.objects.create(
            tenant=tenant,
            domain="reactivated.example.com",
            is_primary=True
        )

        tenant.is_active = True
        tenant.save(update_fields=["is_active"])

        request = self.factory.get(
            "/",
            HTTP_HOST="reactivated.example.com"
        )

        self.middleware(request)

        self.assertEqual(request.tenant, tenant)

    @override_settings(
        ALLOWED_HOSTS=[
            "test-company.example.com",
            "company-b.example.com",
        ]
    )
    def test_middleware_does_not_resolve_wrong_tenant(self):
        tenant_b = Tenant.objects.create(
            name="Company B",
            slug="company-b"
        )

        TenantDomain.objects.create(
            tenant=tenant_b,
            domain="company-b.example.com",
            is_primary=True
        )

        request = self.factory.get(
            "/",
            HTTP_HOST="company-b.example.com"
        )

        self.middleware(request)

        self.assertEqual(request.tenant, tenant_b)
        self.assertNotEqual(request.tenant, self.tenant)
