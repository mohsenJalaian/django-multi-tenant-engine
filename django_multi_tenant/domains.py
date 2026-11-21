from django.db import models, transaction
from django.db.models import Q

from .models import Tenant
from .validators import normalize_domain, validate_domain


class TenantDomain(models.Model):

    tenant = models.ForeignKey(
        Tenant,
        on_delete=models.CASCADE,
        related_name="domains"
    )

    domain = models.CharField(
        max_length=255,
        unique=True,
        validators=[validate_domain],
    )
    is_primary = models.BooleanField(default=False)

    class Meta:
        constraints = [
            models.UniqueConstraint(
                fields=["tenant"],
                condition=Q(is_primary=True),
                name="unique_primary_domain_per_tenant"
            )
        ]

    def clean(self):
        super().clean()
        self.domain = normalize_domain(self.domain)

    def save(self, *args, **kwargs):
        self.domain = normalize_domain(self.domain)

        update_fields = kwargs.get("update_fields")

        if update_fields is not None and "domain" not in update_fields:
            kwargs["update_fields"] = set(update_fields) | {"domain"}

        super().save(*args, **kwargs)

    def __str__(self):
        return self.domain

    def set_as_primary(self):
        with transaction.atomic():
            domain = TenantDomain.objects.select_for_update().get(
                pk=self.pk
            )
            if domain.tenant_id != self.tenant_id:
                raise TenantDomain.DoesNotExist

            Tenant.objects.select_for_update().get(
                pk=domain.tenant_id
            )

            TenantDomain.objects.filter(
                tenant_id=domain.tenant_id,
                is_primary=True
            ).update(is_primary=False)

            domain.is_primary = True
            domain.save(update_fields=["is_primary"])

            self.is_primary = True