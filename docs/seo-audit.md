# SEO and deployment audit

Audit date: 31 October 2026. Scope: every HTML/text source and asset in v2, the older main implementation for comparison, and live URL checks. The working branch starts at v2 commit `b7198bb806e3abf9ce3bd91e5d471cfa14f3b4a7`. No main-branch changes or deployment are part of this work.

## Verified deployment evidence

A direct HTTPS request to `https://mirthuposhan.com/` returned 200 with `server: GitHub.com`, content type `text/html; charset=utf-8` and 79,172 bytes. The live homepage and v2/index.html have the identical SHA-256 hash:

`287677e238f7702fb1916a8061cc303555f56f270ff1871583834e9f1e0c00a5`

The live title was `Mirthu Poshan | Artisanal Malted Nutrition`. Its viewport was valid, but the description, canonical, social tags and structured data were absent. The malformed viewport belonged to the older main/ingredients.html; v2 had no standalone ingredient page.

Live checks found `/index.html`, `/icon.png`, `/package-wider.png`, `/package-cup.png` and `/FULL-logo.jpg` returned 200. `/ingredients.html`, `/about.html`, `/products.html`, `/benefits.html`, `/contact.html`, `/robots.txt`, `/sitemap.xml` and `/icon.jpg` returned 404. A successful homepage response does not prove every deployment setting; the Pages configuration itself was not inspected.

## Findings and changes

| Area | Verified before | Change |
|---|---|---|
| Search metadata | Generic brand title; no description or canonical | Descriptive title, description and absolute canonical on each indexable page |
| Social previews | No Open Graph/Twitter tags | Matching titles, descriptions, canonical URLs and local branded 1200×630 preview |
| Structured data | None | Organization, WebSite, WebPage/CollectionPage, ingredient ItemList and breadcrumbs; no fabricated offers, reviews or nutrition panel |
| Crawling | Robots and sitemap 404 | Sitemap contains only the two canonical pages; robots references it |
| Ingredient page | Live URL 404; malformed viewport in old main page | New static ingredient guide with valid viewport, text, illustrations and linked references |
| Ingredient identity | Wrong category totals; cereals and spices called legumes | 8 millets, 2 nuts, 8 seeds, 20 pulses/legumes, 2 other cereals/starches, 2 spices |
| Ingredient evidence | Hydration, brain-health, complete-protein and other broad claims | Reviewed all 42 recipe entries; conservative food-composition or culinary descriptions and primary citations |
| Allergens | Individual millet gluten claims could mislead | Explicit barley/gluten, peanuts, almonds, walnuts, soy and sesame information |
| Icons | Font Awesome 6.0.0 lacked glyphs such as `fa-nut`; fallback icon.jpg 404 | Local SVG symbols; all references and browser-rendered bounds checked; no broken fallback loop |
| Runtime CSS | Tailwind Play CDN compiles styles in browser | Pinned build dependency, generated static CSS committed |
| Fonts | External stylesheet import on render path | Same typefaces hosted locally with OFL licenses and font-display: swap |
| Images | Hero PNG 1,385,734 bytes; product PNG 885,828 bytes | Compressed WebP derivatives, smaller mobile hero, preload, image dimensions and below-fold lazy loading |
| Content visibility | Reveal content hidden until scrolling | Content visible immediately with JS disabled; no scroll listener needed to expose it |
| Links/navigation | Historical URLs 404; mobile section links hidden | Native mobile menu, working local links, compatibility redirects and 404 fallback |
| Contact form | Unbounded network wait, unlabelled fields, injected notifications, misleading privacy promise | Timeout, status checks, accessible labels/status, preserved failed messages and clear processor disclosure |
| Unsupported marketing | Nutritionally equal to meals, complete nutrition, anonymous stock reviewers, unverified certifications | Removed or replaced with factual product and preparation text |

## Review and operational limits

- The site remains static, with no framework/runtime or database added. Shared ingredient data produces crawlable HTML rather than relying on JavaScript rendering.
- The contact endpoint and public Web3Forms submission identifier already existed in v2. Tests intercept submissions; actual delivery, spam controls and provider account configuration have not been verified. No real message was sent.
- External-link targets are preserved for the business contact channels. Retail ingredient references were not substituted for scientific sources. See the per-ingredient evidence matrix.
- Static hosting controls cache headers, HTTP compression, canonical host redirects and deployment. Those settings cannot be fixed in this HTML PR. Legacy stubs provide immediate HTML redirects rather than HTTP 301s.
- Search Console access, index coverage, backlinks, actual search demand and field Core Web Vitals are unknown. No ranking guarantee or claim of complete SEO optimization is made from a local score.
- Prices, packaging variants, certifications, lab values and infant/medical suitability require business evidence before being added. The obsolete Classic/Kids/Fitness products from main are not carried into this v2 change.
- Rollback is a revert of the change commit on v2. The validation workflow does not deploy, and main is untouched.

## Validation

See the measured results appended below. CI has not been run until GitHub executes the PR workflow. Automated structured-data syntax checks do not replace Google's Rich Results Test or production URL inspection.

- Executed: `npm run build`; `npm test` (6 static regression tests and JavaScript syntax check); `npm run test:browser` (9 browser tests). All passed.
- Browser tests executed in installed Chrome at 375px and 1440px, with JavaScript disabled for crawlable content/SVG checks; contact submissions mocked for success, HTTP error, malformed JSON, network failure and timeout.
- Lighthouse 13.6.0 local mobile simulation on the homepage: SEO **100**, accessibility **100**, performance **100**. These are lab measurements on localhost, not production field metrics or ranking predictions.
- Desktop/mobile screenshots visually inspected; local SVG symbols render. No live contact submission or deployment was performed.
- Ingredient guide: Lighthouse 13.6.0 local mobile simulation: performance **100**, accessibility **100**, seo **100**.
