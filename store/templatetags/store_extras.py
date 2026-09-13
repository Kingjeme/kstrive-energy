from decimal import Decimal, InvalidOperation

from django import template


register = template.Library()


@register.filter
def ngn(value):
    if value is None:
        return "₦0.00"

    try:
        amount = Decimal(str(value))
    except (InvalidOperation, ValueError, TypeError):
        return "₦0.00"

    return f"₦{amount:,.2f}"