# Mirthu Poshan website

A static site for homemade malt flour from Byndoor, Karnataka. This branch is based on `v2`, the branch whose homepage matched the live site during the 31 October 2026 audit. Proposed changes target **v2**, not main. No deployment is performed by the validation workflow.

## Develop and validate

Use Node.js 22 and Python 3.9 or newer:

```sh
npm ci
npm run build
npm test
npx playwright install chromium
npm run test:browser
```

For an installed Chrome browser instead of a Playwright download:

```sh
PLAYWRIGHT_CHROME_PATH='/Applications/Google Chrome.app/Contents/MacOS/Google Chrome' npm run test:browser
```

Preview with `python3 -m http.server 4173 --bind 127.0.0.1`. Browser tests reuse a local preview outside CI. WhatsApp destinations are mocked in tests; tests do not send orders or email.

## Edit content

- `data/ingredients.json` is the source of ingredient names, recipe numbering, nutritional contributions and citations. Keep whole/split and colour variants distinct. Do not replace ingredient composition with claims about the finished product or assign nutrient quantities without a verified product analysis.
- `data/shop.json` contains owner-confirmed pack prices, contacts and FAQ answers. See [the ordering content notes](docs/ordering-content.md) before changing claims or policies.
- `scripts/build_content.py` generates `ingredients.html`, `42ingredients.txt`, metadata and the marked shop, contact, FAQ and ingredient preview blocks of `index.html`. Edit the rest of the homepage directly. The homepage shows six ingredient groups; the guide keeps all 42 entries and references.
- `assets/styles.input.css` contains the Tailwind directives and site styles. `npm run build` produces the committed `assets/site.css`; production uses no runtime CSS compiler.
- `assets/site.js` closes the mobile menu after navigation and opens preparation details for old `#process` links. Ordering links, ingredient text and expandable details work without JavaScript. Orders open a WhatsApp draft or the visitor's email app; the website does not process payments or collect order details.
- Local SVG illustrations are decorative; ingredient names identify each food. They do not purport to be botanical identification photographs. Font licenses are in `assets/fonts/`.
- WebP images are optimized copies of existing repository assets. Original images remain available. The social preview uses an existing branded product image.

Before committing, run the build and tests. The PR workflow checks that generated files remain in sync, validates local links, and runs browser regression tests. Do not place private service credentials or payment secrets in this repository.

## Deployment and SEO follow-up

The generated HTML, CSS, fonts and images are committed so static hosting needs no Node/Python runtime. Keep `CNAME` set to `mirthuposhan.com`. Review and merge into v2 using the existing hosting arrangement. To roll back, revert the change commit on v2; no data migration is involved.

After deployment, verify the canonical homepage, `/ingredients.html`, `/robots.txt` and `/sitemap.xml` return successfully. Submit the sitemap in the domain's Google Search Console property and inspect the two canonical URLs. Review production Core Web Vitals and search performance there; local Lighthouse checks do not establish rankings, index coverage or production field performance.

Historical standalone URLs use immediate HTML redirects plus fallback links to current homepage sections. GitHub Pages does not provide repository-defined HTTP 301 redirects. If hosting later supports server redirects, replace those stubs with HTTP redirects.

See [the SEO audit](docs/seo-audit.md) and [ingredient evidence](docs/ingredient-evidence.md).
