from django.http.request import split_domain_port

from .resolver import get_tenant_from_domain


class TenantMiddleware:

    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):

        domain, _ = split_domain_port(request.get_host())

        request.tenant = get_tenant_from_domain(domain)

        return self.get_response(request)