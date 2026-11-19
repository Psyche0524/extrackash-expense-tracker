from django import template

register = template.Library()


@register.filter
def peso(value):
    """1234.5 -> ₱1,234.50 and -20 -> −₱20.00"""
    if value is None or value == '':
        return ''
    sign = '−' if value < 0 else ''
    return f'{sign}₱{abs(value):,.2f}'
