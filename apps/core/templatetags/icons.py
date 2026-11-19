from django import template
from django.templatetags.static import static
from django.utils.html import format_html

register = template.Library()

# Category and account-type values -> icon names in static/icons/icons.svg. Anything unknown gets 'dots'.
ICONS = {
    'dining': 'food', 'groceries': 'cart', 'transport': 'transport', 'phone': 'phone', 'bills': 'bills',
    'subscriptions': 'repeat', 'shopping': 'bag', 'fun': 'fun', 'health': 'health', 'fees': 'percent',
    'salary': 'briefcase', 'bonus': 'gift', 'freelance': 'laptop', 'commission': 'percent', 'business': 'store',
    'side_hustle': 'zap', 'allowance': 'wallet', 'gift': 'gift', 'refund': 'refund', 'cashback': 'coins',
    'interest': 'invest', 'dividend': 'budget', 'rental': 'home', 'transfer': 'swap',
    'bank': 'bank', 'wallet': 'phone', 'cash': 'cash', 'credit': 'card',
}


@register.simple_tag
def icon(name, label=''):
    """<svg> pointing at a symbol in static/icons/icons.svg. Decorative unless a label is given."""
    href = f"{static('icons/icons.svg')}#i-{name}"
    if label:
        return format_html('<svg class="i" role="img" aria-label="{}"><use href="{}"/></svg>', label, href)
    return format_html('<svg class="i" aria-hidden="true"><use href="{}"/></svg>', href)


@register.filter
def icon_for(value):
    return ICONS.get(value, 'dots')
