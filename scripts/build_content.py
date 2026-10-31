"""Render the reviewed ingredient data into static, crawlable HTML (stdlib only)."""
from pathlib import Path
from html import escape
import json
import re

ROOT = Path(__file__).resolve().parents[1]
ORIGIN = 'https://mirthuposhan.com'
DATA = json.loads((ROOT / 'data/ingredients.json').read_text())
CATEGORIES = ['Millets', 'Nuts', 'Seeds', 'Pulses and legumes', 'Other cereals and starches', 'Spices']


def icon(name):
    return (f'<svg class="site-icon ingredient-icon" aria-hidden="true" width="48" height="48">'
            f'<use href="/assets/ingredients.svg#{escape(name)}"></use></svg>')


def cards(detailed=False):
    groups = []
    for category in CATEGORIES:
        members = [i for i in DATA['ingredients'] if i['category'] == category]
        group = f'<h3 class="category-title">{escape(category)} ({len(members)})</h3>\n<div class="ingredient-grid">\n'
        for item in members:
            ident = escape(item['id'])
            group += f'<article class="ingredient-detail" id="{ident}">\n{icon(item["icon"])}\n'
            group += f'<h4>{escape(item["name"])}</h4>\n<p><strong>{escape(item["nutrient"])}</strong></p>\n'
            if detailed:
                group += f'<p>{escape(item["detail"])}</p>\n'
                if item['sources']:
                    group += '<p class="text-sm">Sources: ' + ', '.join(
                        f'<a href="#source-{key}">{escape(DATA["sources"][key]["title"])}</a>'
                        for key in item['sources']) + '</p>\n'
                else:
                    group += '<p><a href="/#contact">Ask about this ingredient</a></p>\n'
            else:
                group += f'<p><a href="/ingredients.html#{ident}">Read about {escape(item["name"])}</a></p>\n'
            group += '</article>\n'
        groups.append(group + '</div>\n')
    return '\n'.join(groups)


def metadata(title, description, path, page_type='WebPage'):
    url = ORIGIN + path
    graph = [
        {'@type': 'Organization', '@id': ORIGIN + '/#organization', 'name': 'Mirthu Poshan',
         'url': ORIGIN + '/', 'logo': ORIGIN + '/icon.png', 'telephone': '+91-91481-09589',
         'sameAs': ['https://instagram.com/mirthu_poshan'],
         'address': {'@type': 'PostalAddress', 'streetAddress': '9-196 Kaluvadi Post Mayyadi',
                     'addressLocality': 'Byndoor', 'addressRegion': 'Karnataka',
                     'postalCode': '576214', 'addressCountry': 'IN'}},
        {'@type': 'WebSite', '@id': ORIGIN + '/#website', 'url': ORIGIN + '/',
         'name': 'Mirthu Poshan', 'publisher': {'@id': ORIGIN + '/#organization'}},
        {'@type': page_type, '@id': url + '#webpage', 'url': url, 'name': title,
         'description': description, 'inLanguage': 'en-IN',
         'isPartOf': {'@id': ORIGIN + '/#website'}, 'publisher': {'@id': ORIGIN + '/#organization'}}
    ]
    if path == '/ingredients.html':
        graph.append({'@type': 'BreadcrumbList', 'itemListElement': [
            {'@type': 'ListItem', 'position': 1, 'name': 'Home', 'item': ORIGIN + '/'},
            {'@type': 'ListItem', 'position': 2, 'name': 'Ingredients', 'item': url}]})
        graph.append({'@type': 'ItemList', 'name': '42 listed recipe ingredients',
                      'numberOfItems': 42, 'itemListElement': [
                          {'@type': 'ListItem', 'position': n, 'name': i['name'], 'url': url + '#' + i['id']}
                          for n, i in enumerate(DATA['ingredients'], 1)]})
    preload = '' if path != '/' else '<link rel="preload" as="image" href="/assets/hero-mobile.webp" media="(max-width: 767px)" fetchpriority="high"><link rel="preload" as="image" href="/assets/hero.webp" media="(min-width: 768px)" fetchpriority="high">'
    return f'''<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>{escape(title)}</title>
<meta name="description" content="{escape(description)}">
<meta name="robots" content="index,follow,max-image-preview:large">
<link rel="canonical" href="{url}">
<meta property="og:type" content="website">
<meta property="og:locale" content="en_IN">
<meta property="og:site_name" content="Mirthu Poshan">
<meta property="og:title" content="{escape(title)}">
<meta property="og:description" content="{escape(description)}">
<meta property="og:url" content="{url}">
<meta property="og:image" content="{ORIGIN}/assets/social-preview.jpg">
<meta property="og:image:width" content="1200">
<meta property="og:image:height" content="630">
<meta property="og:image:alt" content="Mirthu Poshan malt flour packaging">
<meta name="twitter:card" content="summary_large_image">
<meta name="twitter:title" content="{escape(title)}">
<meta name="twitter:description" content="{escape(description)}">
<meta name="twitter:image" content="{ORIGIN}/assets/social-preview.jpg">
<meta name="twitter:image:alt" content="Mirthu Poshan malt flour packaging">
<meta name="theme-color" content="#3a5a40">
<link rel="icon" href="/icon.png" type="image/png">
<link rel="stylesheet" href="/assets/site.css">
{preload}
<script type="application/ld+json">{json.dumps({'@context': 'https://schema.org', '@graph': graph}, ensure_ascii=False).replace('<', chr(92) + 'u003c')}</script>
</head>'''


def build():
    (ROOT / '42ingredients.txt').write_text('Mirthu Poshan — 42 listed recipe ingredients\n\n' + '\n'.join(f'{i["recipe_position"]}. {i["name"]}' for i in sorted(DATA['ingredients'], key=lambda row: row['recipe_position'])) + '\n')
    homepage = (ROOT / 'index.html').read_text()
    homepage = re.sub(r'<head>.*?</head>', lambda _: metadata(
        'Mirthu Poshan | Homemade Malt Flour with 42 Ingredients',
        'Explore Mirthu Poshan homemade malt flour from Byndoor, Karnataka. Discover 42 listed ingredients, preparation guidance and contact us to order.', '/'), homepage, flags=re.S)
    homepage = re.sub(r'<!-- INGREDIENTS:START -->.*?<!-- INGREDIENTS:END -->',
                      lambda _: '<!-- INGREDIENTS:START -->\n' + cards() + '<!-- INGREDIENTS:END -->', homepage, flags=re.S)
    (ROOT / 'index.html').write_text(homepage)
    sources = '<ul class="source-list space-y-4">' + ''.join(
        f'<li id="source-{key}"><a href="{escape(source["url"])}">{escape(source["title"])}</a></li>'
        for key, source in DATA['sources'].items()) + '</ul>'
    ingredients = '<!DOCTYPE html>\n<html lang="en-IN">\n' + metadata(
        '42 Ingredients & Nutrition Guide | Mirthu Poshan Malt Flour',
        'Explore the 42 ingredients listed in Mirthu Poshan malt flour: millets, pulses, nuts, seeds and spices, with sourced nutrition notes and allergen information.',
        '/ingredients.html', 'CollectionPage') + '''
<body class="bg-[#f8f6f0]">
<a href="#main-content" class="skip-link">Skip to content</a>
<header class="bg-white border-b border-stone-200"><nav aria-label="Main navigation" class="max-w-7xl mx-auto px-6 py-6 flex flex-wrap gap-6 items-center">
<a href="/" class="font-bold text-[#3a5a40]">Mirthu Poshan</a><a href="/#about">Our story</a><a href="/ingredients.html" aria-current="page">Ingredients</a><a href="/#usage">Preparation</a><a href="/#contact">Contact and orders</a></nav></header>
<main id="main-content" class="max-w-7xl mx-auto px-6 py-16">
<nav aria-label="Breadcrumb" class="mb-8"><a href="/" class="underline">Home</a> / Ingredients</nav>
<h1 class="text-4xl lg:text-6xl font-bold serif text-[#3a5a40] mb-8">The 42 Ingredients in Mirthu Poshan Malt Flour</h1>
<p class="text-lg leading-relaxed">Explore the ingredients listed in our recipe and the nutrients or culinary qualities they contribute. Whole, split and colour variants are listed separately, as in the recipe.</p>
<div class="nutrition-note"><h2 class="text-xl font-bold">Understanding these nutrition notes</h2>
<p>These sources describe individual foods, not laboratory results for Mirthu Poshan. The amount in a serving depends on the recipe proportions, processing and preparation. This flour complements a varied diet and is not a meal replacement or a treatment for any medical condition.</p>
<p><strong>Allergens:</strong> the listed recipe includes barley (gluten), peanuts, almonds, walnuts, soy and sesame. This blend is not gluten-free. Contact us about allergen handling before ordering.</p></div>
<h2 class="text-3xl font-bold text-[#3a5a40] mt-12">Ingredient guide</h2>
''' + cards(True) + '''
<section class="mt-16" aria-labelledby="sources-title"><h2 id="sources-title" class="text-3xl font-bold text-[#3a5a40] mb-6">Nutrition references</h2>
<p class="mb-6">Reviewed on 31 October 2026. Food-composition tables support nutrient descriptions; they do not establish a clinical benefit for this blend. Local ingredient names and whole or split forms follow the recipe details confirmed by the maker.</p>
''' + sources + '''</section>
<p class="mt-12"><a href="/#contact" class="btn-primary inline-block px-8 py-4 rounded-2xl font-bold">Ask about ingredients or place an order</a></p>
</main>
<footer class="bg-white px-6 py-8 text-center"><a href="/">Mirthu Poshan home</a> · <a href="/#contact">Contact</a></footer>
</body></html>
'''
    (ROOT / 'ingredients.html').write_text(ingredients)


if __name__ == '__main__':
    build()
