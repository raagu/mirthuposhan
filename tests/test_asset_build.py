"""Ensure asset updates get new URLs without breaking previously cached pages."""
import importlib.util
from pathlib import Path
import re
import tempfile
import unittest
from unittest.mock import patch

script = Path(__file__).resolve().parents[1] / 'scripts/version_assets.py'
spec = importlib.util.spec_from_file_location('version_assets', script)
version_assets = importlib.util.module_from_spec(spec)
spec.loader.exec_module(version_assets)


class AssetBuildTest(unittest.TestCase):
    def test_changed_assets_get_new_urls_and_old_versions_remain_available(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            (root / 'assets').mkdir()
            page = root / 'index.html'
            page.write_text('<link rel="stylesheet" href="/assets/site.css">'
                            '<script src="/assets/site.js"></script>')
            for extension in ('css', 'js'):
                (root / 'assets' / f'site.{extension}').write_text('/* first release */')
            with patch.object(version_assets, 'ROOT', root):
                version_assets.build()
                old_urls = re.findall(r'(?:href|src)="([^"]+)"', page.read_text())
                for extension in ('css', 'js'):
                    (root / 'assets' / f'site.{extension}').write_text('/* second release */')
                version_assets.build()
                new_urls = re.findall(r'(?:href|src)="([^"]+)"', page.read_text())
                self.assertEqual(len(new_urls), 2)
                self.assertTrue(set(old_urls).isdisjoint(new_urls))
                for urls, content in [(old_urls, '/* first release */'),
                                      (new_urls, '/* second release */')]:
                    for url in urls:
                        self.assertEqual((root / url.lstrip('/')).read_text(), content)
                snapshot = {p.relative_to(root): p.read_bytes() for p in root.rglob('*') if p.is_file()}
                version_assets.build()
                self.assertEqual(snapshot, {p.relative_to(root): p.read_bytes()
                                           for p in root.rglob('*') if p.is_file()})
