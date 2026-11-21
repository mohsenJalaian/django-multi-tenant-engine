from django.core.exceptions import ValidationError

from .domains import TenantDomain
from .validators import normalize_domain


def get_tenant_from_domain(domain):
    try:
        domain = normalize_domain(domain)

        tenant_domain = TenantDomain.objects.select_related(
            "tenant"
        ).get(
            domain=domain,
            tenant__is_active=True
        )

        return tenant_domain.tenant

    except (TenantDomain.DoesNotExist, ValidationError):
        return None