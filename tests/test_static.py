import re
from pathlib import Path

from django.conf import settings
from django.test import SimpleTestCase

from apps.core.templatetags.icons import ICONS

STATIC = Path(settings.BASE_DIR) / 'static'


class StaticAssetTests(SimpleTestCase):
    def test_every_icon_used_has_a_file(self):
        used = set(ICONS.values()) | {'dots'}
        for template in (Path(settings.BASE_DIR) / 'templates').rglob('*.html'):
            used |= set(re.findall(r"\{% icon '([\w-]+)'", template.read_text(encoding='utf-8')))
        missing = sorted(name for name in used if not (STATIC / 'icons' / f'{name}.svg').exists())
        self.assertEqual(missing, [], 'add these to static/icons/')

    def test_css_and_template_assets_exist(self):
        css = (STATIC / 'css' / 'style.css').read_text(encoding='utf-8')
        for ref in re.findall(r"url\('\.\./([^']+)'\)", css):
            self.assertTrue((STATIC / ref).exists(), ref)
        for template in (Path(settings.BASE_DIR) / 'templates').rglob('*.html'):
            for ref in re.findall(r"\{% static '([^']+)' %\}", template.read_text(encoding='utf-8')):
                self.assertTrue((STATIC / ref).exists(), f'{template.name}: {ref}')
