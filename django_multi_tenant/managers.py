from django.db import models


class TenantQuerySet(models.QuerySet):

    def active(self):
        return self.filter(is_active=True)

    def inactive(self):
        return  self.filter(is_active=False)
    def by_slug(self, slug):
        return self.filter(slug=slug)