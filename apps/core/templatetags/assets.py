import os

from django import template
from django.contrib.staticfiles import finders
from django.templatetags.static import static

register = template.Library()


@register.simple_tag
def asset(path):
    """Static URL plus ?v=<last modified time>, so browsers fetch new CSS/JS as soon as it changes."""
    found = finders.find(path)
    return f'{static(path)}?v={int(os.path.getmtime(found))}' if found else static(path)
