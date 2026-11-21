from django.http import JsonResponse


def current_tenant(request):

    if request.tenant is None:
        return JsonResponse(
            {"error": "Tenant not found"},
            status=404
        )

    return JsonResponse({
        "tenant_name": request.tenant.name,
        "tenant_slug": request.tenant.slug,
    })