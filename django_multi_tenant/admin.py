from django import forms
from django.contrib import admin

from .domains import TenantDomain
from .models import Tenant


class TenantDomainAdminForm(forms.ModelForm):

    def _get_validation_exclusions(self):
        exclude = super()._get_validation_exclusions()
        exclude.add("tenant")
        return exclude

    class Meta:
        model = TenantDomain
        fields = "__all__"


class TenantDomainInline(admin.TabularInline):

    model = TenantDomain
    form = TenantDomainAdminForm
    extra = 1


@admin.register(Tenant)
class TenantAdmin(admin.ModelAdmin):

    list_display = (
        "name",
        "slug",
        "is_active",
        "created_at",
    )

    list_filter = (
        "is_active",
    )

    search_fields = (
        "name",
        "slug",
    )

    ordering = (
        "-created_at",
    )
    inlines = (TenantDomainInline,)

    def save_formset(self, request, form, formset, change):

        instances = formset.save(commit=False)

        for obj in formset.deleted_objects:
            obj.delete()

        for obj in instances:
            should_be_primary = obj.is_primary

            if should_be_primary:
                obj.is_primary = False

            obj.save()

            if should_be_primary:
                obj.set_as_primary()

        formset.save_m2m()

@admin.register(TenantDomain)
class TenantDomainAdmin(admin.ModelAdmin):

    form = TenantDomainAdminForm

    list_display = (
        "domain",
        "tenant",
        "is_primary",
    )

    list_filter = (
        "is_primary",
    )

    search_fields = (
        "domain",
        "tenant__name",
    )

    list_select_related = (
        "tenant",
    )

    def save_model(self, request, obj, form, change):
        should_be_primary = obj.is_primary

        obj.is_primary = False

        super().save_model(request, obj, form, change)

        if should_be_primary:
            obj.set_as_primary()

