from django.db import models

from .managers import TenantQuerySet

class Tenant(models.Model):
    objects = TenantQuerySet.as_manager()

    name = models.CharField(max_length=100)
    slug = models.SlugField(unique=True)
    created_at = models.DateTimeField(auto_now_add=True)
    is_active = models.BooleanField(default=True)
    updated_at = models.DateTimeField(auto_now=True)

    @property
    def primary_domain(self):
        if "domains" in getattr(self, "_prefetched_objects_cache", {}):
            return next(
                (
                    domain
                    for domain in self._prefetched_objects_cache["domains"]
                    if domain.is_primary
                ),
                None
            )

        return self.domains.filter(is_primary=True).first()

    def __str__(self):
        return self.name
from .domains import TenantDomain
__all__ = ["Tenant", "TenantDomain"]