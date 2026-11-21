# Django Multi-Tenant Engine

A reusable multi-tenant engine for Django applications.

## Overview

Django Multi-Tenant Engine is an open-source project designed to help developers build Django applications that serve multiple independent organizations from a shared application.

Each organization, or tenant, should have access only to its own data.

## Planned Features


## Features

- Tenant and organization management
- Multiple domains for each tenant
- Primary domain management
- Automatic domain normalization
- Internationalized domain support (IDN)
- Tenant resolution based on request domain
- Middleware integration through `request.tenant`
- Support for active and inactive tenants
- Django Admin integration
- Current tenant API endpoint
- Automated test suite

## Installation

Install the package using pip:

```bash
pip install django-multi-tenant-engine
```

## Requirements

- Python 3.11 or later
- Django 5.2 or later

## Configuration

Add `django_multi_tenant` to your `INSTALLED_APPS`:

```python
INSTALLED_APPS = [
    # ...
    "django_multi_tenant",
]
```

Add `TenantMiddleware` to your `MIDDLEWARE` setting:

```python
MIDDLEWARE = [
    # ...
    "django_multi_tenant.middleware.TenantMiddleware",
]
```

Make sure `TenantMiddleware` is placed before any middleware or application component that needs access to `request.tenant`.

Run migrations:

```bash
python manage.py migrate
```

## Tenant and Domain Management

Each tenant represents an independent organization.

You can create tenants using Django's ORM:

```python
from django_multi_tenant.models import Tenant, TenantDomain

tenant = Tenant.objects.create(
    name="Example Company",
    slug="example-company",
)

TenantDomain.objects.create(
    tenant=tenant,
    domain="example.com",
    is_primary=True,
)
```

A tenant can have multiple domains, but only one primary domain.

Domains are automatically normalized when saved. Internationalized domain names (IDNs) are also supported.

## Accessing the Current Tenant

After `TenantMiddleware` resolves the request domain, the current tenant is available through `request.tenant`.

Example:

```python
def my_view(request):
    tenant = request.tenant

    if tenant is None:
        return HttpResponseNotFound("Tenant not found")

    return JsonResponse({
        "tenant_name": tenant.name,
        "tenant_slug": tenant.slug,
    })# Django Multi-Tenant Engine

A reusable domain-based multi-tenant engine for Django applications.

Django Multi-Tenant Engine helps Django developers identify the tenant associated with an incoming request based on its domain or subdomain.

It provides tenant management, multiple domain support, automatic domain normalization, middleware integration, and Django Admin integration.

## Features

- Tenant and organization management
- Multiple domains for each tenant
- Primary domain management
- Automatic domain normalization
- Internationalized Domain Name (IDN) support
- Tenant resolution based on request domains
- Middleware integration through `request.tenant`
- Support for active and inactive tenants
- Django Admin integration
- Current tenant JSON endpoint
- Automated test suite

## Requirements

- Python 3.11 or later
- Django 5.2 or later

## Installation

Install the package using pip:

```bash
pip install django-multi-tenant-engine
```

## Configuration

### 1. Add the application

Add `django_multi_tenant` to your `INSTALLED_APPS`:

```python
INSTALLED_APPS = [
    # ...
    "django_multi_tenant",
]
```

### 2. Configure the middleware

Add `TenantMiddleware` to your `MIDDLEWARE` setting:

```python
MIDDLEWARE = [
    "django.middleware.security.SecurityMiddleware",
    "django_multi_tenant.middleware.TenantMiddleware",
    # ...
]
```

Place `TenantMiddleware` before any middleware or application component that needs access to `request.tenant`.

### 3. Configure allowed hosts

Django's `ALLOWED_HOSTS` setting must allow the domains used by your tenants.

For example:

```python
ALLOWED_HOSTS = [
    "example.com",
    "tenant1.example.com",
    "tenant2.example.com",
]
```

Do not use `ALLOWED_HOSTS = ["*"]` as a substitute for proper host validation.

### 4. Run migrations

```bash
python manage.py migrate
```

## Tenant and Domain Management

Each tenant represents an independent organization.

You can create a tenant using Django's ORM:

```python
from django_multi_tenant.models import Tenant, TenantDomain

tenant = Tenant.objects.create(
    name="Example Company",
    slug="example-company",
)

TenantDomain.objects.create(
    tenant=tenant,
    domain="example.com",
    is_primary=True,
)
```

A tenant can have multiple domains, but only one domain can be marked as primary.

Domains are automatically normalized when saved. Internationalized domain names are also supported and stored in their normalized ASCII representation.

### Primary Domain

You can retrieve a tenant's primary domain using the `primary_domain` property:

```python
tenant = Tenant.objects.get(slug="example-company")

print(tenant.primary_domain)
```

To change a domain to the primary domain:

```python
domain = TenantDomain.objects.get(
    domain="example.com"
)

domain.set_as_primary()
```

## Accessing the Current Tenant

After `TenantMiddleware` resolves the incoming request domain, the current tenant is available through `request.tenant`.

Example:

```python
from django.http import HttpResponseNotFound, JsonResponse

def my_view(request):
    tenant = request.tenant

    if tenant is None:
        return HttpResponseNotFound("Tenant not found")

    return JsonResponse({
        "tenant_name": tenant.name,
        "tenant_slug": tenant.slug,
    })
```

If the request domain does not match an active tenant, `request.tenant` will be `None`.

The middleware does not automatically block requests without a tenant. Your application is responsible for handling these requests.

## URL Configuration

You can include the library's URL configuration in your project's root `urls.py`:

```python
from django.urls import include, path

urlpatterns = [
    path("", include("django_multi_tenant.urls")),
]
```

## Important: Data Isolation

Django Multi-Tenant Engine focuses on tenant identification and domain resolution.

It does **not** automatically filter queries or isolate data belonging to different tenants.

Your application is responsible for enforcing tenant-level data isolation.

For example, when retrieving tenant-specific records, always apply the appropriate tenant filter:

```python
records = MyModel.objects.filter(
    tenant=request.tenant
)
```

Make sure your application also handles authentication, authorization, and access control appropriately.

## Domain Ownership and Security

Registering a domain in the database does not verify its ownership.

Before associating a domain with a tenant, your application administrator must verify that the domain is controlled by the intended organization.

The library relies on Django's host validation through `ALLOWED_HOSTS` and uses Django's `request.get_host()` when resolving the request domain.

## Running Tests

To run the project's test suite:

```bash
python -m django test django_multi_tenant.tests --settings=test_settings -v 2
```

The project includes automated tests for:

- Tenant models and domain management
- Domain validation and normalization
- Tenant resolution
- Middleware behavior
- Django Admin integration
- Tenant views

## Technology Stack

- Python
- Django
- SQLite for the development test configuration
- Django's built-in testing framework
- Ruff for code quality checks

## Project Status

Version `0.1.0` is under development.

The initial release focuses on tenant management, domain-based tenant resolution, and middleware integration.

## License

This project is licensed under the MIT License. See the [LICENSE](LICENSE) file for details.
```

If the request domain does not match an active tenant, `request.tenant` will be `None`.

The middleware does not automatically block requests without a tenant. Your application is responsible for handling these requests.

## Project Status

This project is currently under development. Features will be implemented and tested incrementally.

## Technology Stack

- Python
- Django
- pytest or Django's built-in testing framework

## License

License information will be added before the first public release.