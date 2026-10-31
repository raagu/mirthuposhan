"""Regression checks for crawlability, references, metadata and local resources."""
import json
from hashlib import sha256
from pathlib import Path
from html.parser import HTMLParser
from urllib.parse import urlsplit, unquote, parse_qs
import unittest
import xml.etree.ElementTree as ET

ROOT = Path(__file__).resolve().parents[1]


class Document(HTMLParser):
    def __init__(self, content):
        super().__init__()
        self.tags = []
        self.ids = []
        self.jsonld = []
        self.script_type = None
        self.feed(content)

    def handle_starttag(self, tag, attributes):
        attrs = dict(attributes)
        self.tags.append((tag, attrs))
        if 'id' in attrs:
            self.ids.append(attrs['id'])
        if tag == 'script':
            self.script_type = attrs.get('type')

    def handle_endtag(self, tag):
        if tag == 'script':
            self.script_type = None

    def handle_data(self, text):
        if self.script_type == 'application/ld+json':
            self.jsonld.append(json.loads(text))

    def find(self, tag, **attrs):
        return [a for t, a in self.tags if t == tag and all(a.get(k) == v for k, v in attrs.items())]


class SiteTest(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.documents = {p.name: Document(p.read_text()) for p in ROOT.glob('*.html')}
        cls.data = json.loads((ROOT / 'data/ingredients.json').read_text())

    def test_indexable_page_metadata(self):
        for name, canonical in [('index.html', 'https://mirthuposhan.com/'),
                                ('ingredients.html', 'https://mirthuposhan.com/ingredients.html')]:
            with self.subTest(page=name):
                doc = self.documents[name]
                self.assertEqual(len(doc.find('title')), 1)
                self.assertEqual(len(doc.find('h1')), 1)
                self.assertEqual(len(doc.find('main')), 1)
                self.assertEqual(doc.find('meta', name='viewport')[0]['content'],
                                 'width=device-width, initial-scale=1.0')
                self.assertEqual(doc.find('link', rel='canonical')[0]['href'], canonical)
                self.assertEqual(doc.find('meta', property='og:url')[0]['content'], canonical)
                self.assertTrue(doc.find('meta', name='description')[0]['content'])
                for tag in ['og:title', 'og:description', 'og:image']:
                    self.assertTrue(doc.find('meta', property=tag)[0]['content'])
                self.assertEqual(doc.find('meta', name='twitter:card')[0]['content'], 'summary_large_image')
                self.assertEqual(len(doc.jsonld), 1)
                self.assertTrue(doc.jsonld[0]['@graph'])

    def test_every_local_link_asset_and_svg_symbol_exists(self):
        for name, doc in self.documents.items():
            self.assertEqual(len(doc.ids), len(set(doc.ids)), f'Duplicate id in {name}')
            for tag, attrs in doc.tags:
                for key in ('href', 'src'):
                    if key not in attrs:
                        continue
                    url = urlsplit(attrs[key])
                    if url.scheme or url.netloc:
                        continue
                    self.assertNotEqual(attrs[key], '#', f'Placeholder in {name}')
                    path = ROOT / ('index.html' if url.path == '/' else (unquote(url.path).lstrip('/') or name))
                    if path.is_dir():
                        path /= 'index.html'
                    self.assertTrue(path.is_file(), f'{name}: missing {path}')
                    if url.fragment:
                        if path.suffix == '.html':
                            self.assertIn(url.fragment, self.documents[path.name].ids)
                        elif path.suffix == '.svg':
                            ids = {e.get('id') for e in ET.parse(path).iter()}
                            self.assertIn(url.fragment, ids)
                if tag == 'a' and attrs.get('target') == '_blank':
                    self.assertIn('noopener', attrs.get('rel', ''))

    def test_all_42_recipe_entries_are_static_and_referenced(self):
        items = self.data['ingredients']
        self.assertEqual(len(items), 42)
        self.assertEqual(len({i['id'] for i in items}), 42)
        self.assertEqual(sorted(i['recipe_position'] for i in items), list(range(1, 43)))
        for item in items:
            self.assertIn(item['id'], self.documents['ingredients.html'].ids)
            if item['status'] == 'reviewed':
                self.assertTrue(item['sources'])
                self.assertTrue(item['reference_entry'])
            else:
                self.assertEqual(item['status'], 'identity-unconfirmed')
                self.assertFalse(item['sources'])
                self.assertIn('confirm', item['detail'])
            for source in item['sources']:
                self.assertIn('source-' + source, self.documents['ingredients.html'].ids)
        lists = [n for n in self.documents['ingredients.html'].jsonld[0]['@graph'] if n['@type'] == 'ItemList']
        self.assertEqual(len(lists[0]['itemListElement']), 42)

    def test_sitemap_and_robots_agree_with_canonicals(self):
        ns = {'s': 'http://www.sitemaps.org/schemas/sitemap/0.9'}
        urls = ET.parse(ROOT / 'sitemap.xml').findall('s:url/s:loc', ns)
        self.assertEqual({u.text for u in urls}, {
            'https://mirthuposhan.com/', 'https://mirthuposhan.com/ingredients.html'})
        self.assertIn('Sitemap: https://mirthuposhan.com/sitemap.xml', (ROOT / 'robots.txt').read_text())

    def test_images_and_content_are_progressively_enhanced(self):
        for name in ('index.html', 'ingredients.html'):
            doc = self.documents[name]
            for image in doc.find('img'):
                self.assertTrue(image.get('alt'))
                self.assertGreater(int(image['width']), 0)
                self.assertGreater(int(image['height']), 0)
                self.assertNotIn('onerror', image)
            self.assertNotIn('cdn.tailwindcss.com', (ROOT / name).read_text())
            self.assertNotIn('font-awesome', (ROOT / name).read_text())
        css = (ROOT / 'assets/styles.input.css').read_text()
        self.assertNotIn('opacity: 0;', css)
        form = self.documents['index.html']
        self.assertFalse(form.find('form'), 'Orders should use direct WhatsApp/email links')
        self.assertTrue(form.find('a', href='/ingredients.html'))

    def test_pack_prices_and_order_destinations(self):
        home = self.documents['index.html']
        for label, price in [('500 g', '₹300'), ('1 kg', '₹600')]:
            name = f'Order on WhatsApp: {label} for {price}'
            link = home.find('a', **{'aria-label': name})[0]
            url = urlsplit(link['href'])
            self.assertEqual(url.netloc, 'wa.me')
            self.assertEqual(url.path, '/919148109589')
            message = parse_qs(url.query)['text'][0]
            self.assertIn(f'({label}, {price})', message)
            self.assertIn('delivery PIN code', message)
        email_links = [a for a in home.find('a') if a.get('href', '').startswith('mailto:')]
        self.assertTrue(email_links)
        for link in email_links:
            url = urlsplit(link['href'])
            self.assertEqual(url.path, 'mirthuposhan@gmail.com')
            self.assertEqual(parse_qs(url.query)['subject'], ['Mirthu Poshan order'])
            self.assertNotIn('+', url.query, 'Mail clients require percent-encoded spaces')

    def test_homepage_preview_and_collapsed_information(self):
        home = self.documents['index.html']
        categories = [a for a in home.find('a') if 'category-card' in a.get('class', '').split()]
        self.assertEqual(len(categories), 6)
        self.assertFalse(home.find('article', **{'class': 'ingredient-detail'}))
        self.assertEqual(len(self.documents['ingredients.html'].find('article')), 42)
        faqs = [a for a in home.find('details') if 'faq-item' in a.get('class', '').split()]
        self.assertEqual(len(faqs), 7)
        self.assertTrue(all('open' not in a for a in home.find('details')))
        source = (ROOT / 'index.html').read_text()
        self.assertIn('https://share.google/eFBwM7jvW1bbd8ieB', source)
        self.assertNotIn('info@mirthuposhan.com', source)
        self.assertNotIn('api.web3forms.com', source)
        self.assertIn('<title>Mirthu Poshan | Homemade Malt Flour with 42 Ingredients</title>', source)

    def test_historical_urls_continue_to_live_sections(self):
        for name in ('about.html', 'products.html', 'benefits.html', 'contact.html'):
            doc = self.documents[name]
            refresh = doc.find('meta', **{'http-equiv': 'refresh'})[0]['content']
            fragment = refresh.split('#')[1]
            self.assertIn(fragment, self.documents['index.html'].ids)
            self.assertEqual(doc.find('meta', name='robots')[0]['content'], 'noindex,follow')

    def test_pages_reference_the_matching_versioned_styles_and_scripts(self):
        for name, doc in self.documents.items():
            for tag, attrs in doc.tags:
                for key in ('href', 'src'):
                    url = urlsplit(attrs.get(key, ''))
                    if not url.path.startswith('/assets/site.'):
                        continue
                    extension = Path(url.path).suffix
                    source = (ROOT / 'assets' / ('site' + extension)).read_bytes()
                    digest = sha256(source).hexdigest()[:16]
                    self.assertEqual(url.path, f'/assets/site.{digest}{extension}', name)
                    self.assertEqual((ROOT / url.path.lstrip('/')).read_bytes(), source)
                    self.assertFalse(url.query, 'Use distinct paths, not cache-dependent query strings')


if __name__ == '__main__':
    unittest.main()
