import re

from django.core.exceptions import ValidationError


def years_interval_validator(value):
    pattern = '^\d{4} - \d{4}$'
    if not re.match(pattern, value):
        raise ValidationError(
            message=f"{value} does not mathc the pattern for years interval",
            params={'value': value,
                    'pattern': pattern,
                    }
        )


def percentage_validator(value):
    if value > 100 or value < 0:
        raise ValidationError(
            message=f"{value} must be in 0 - 100 interval",
            params={'value': value}
        )