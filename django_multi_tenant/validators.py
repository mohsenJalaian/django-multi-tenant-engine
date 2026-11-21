from django.core.exceptions import ValidationError
from django.core.validators import DomainNameValidator

validate_domain = DomainNameValidator(
    accept_idna=True
)


def normalize_domain(domain):
    if not isinstance(domain, str):
        raise ValidationError(
            "Enter a valid domain name."
        )

    domain = domain.strip().lower()

    # Reject multiple trailing dots
    if domain.endswith(".."):
        raise ValidationError(
            "Enter a valid domain name."
        )

    # Remove a single trailing dot
    domain = domain.removesuffix(".")

    try:
        domain = domain.encode("idna").decode("ascii")
        validate_domain(domain)

        return domain

    except (UnicodeError, ValidationError) as exc:
        raise ValidationError(
            "Enter a valid domain name."
        ) from exc
