# Ordering content and review notes

These business details were supplied by the owner in the website intake. They are not independent product laboratory results. Nutrition notes remain separately sourced in `data/ingredients.json` and the ingredient guide.

## Confirmed details

- 500 g costs ₹300; 1 kg costs ₹600.
- The Early Bird offer gives free delivery across India until the owner announces a change. No closing date was supplied.
- Orders use WhatsApp +91 91481 09589 or mirthuposhan@gmail.com. Enquiry hours are 8 AM–10 PM IST every day.
- Courier orders use UPI. Cash is available for pickup or delivery by the maker's own team, depending on location and PIN code. There is no promise of courier cash on delivery.
- The blend is prepared after taking orders and dispatched within one week of confirmation, usually within 2–3 days of preparation. Transit time depends on the destination; no delivery date is promised.
- The owner specified six months **after opening**, stored in an airtight container. Do not silently rewrite this as six months from preparation. The pack carries a preparation date.
- Preparation uses 1–2 tablespoons per glass of milk or water. Exact cooking time, serving grams and glass volume were not supplied; readers are directed to the pack instructions. No measuring scoop is included.
- The taste is mildly roasted. Jaggery or a pinch of salt is optional; the owner says to avoid salt with milk.
- The process is cleaning, sun-drying, winnowing the ingredients, roasting over heat, grinding, sieving out coarse particles, then packing and dispatching. No duration is assigned to individual steps.
- A replacement or refund is available for damaged or incorrect packs. No reporting deadline was supplied.
- The family has made and consumed this blend for 2–3 years. The family and team now prepare it for others.
- The owner supplied the Google Business Profile review link. The site links to it without inventing review text, a star rating or a review count.

## Compact page and preserved content

Prices and pack-specific WhatsApp drafts appear at the top. Email is a secondary option. The homepage shows six ingredient categories linking to the full, referenced 42-ingredient guide. Seven FAQs, preparation process and pickup address use closed native details elements so visitors choose what to read.

The approved title, 42 ingredients / 72h slow-crafted / 0% added sugars / 0% additives highlights and both comparison images are preserved. These highlights are owner-approved descriptions, not new nutritional analysis. No claim is added that one glass supplies every nutrient or replaces a varied diet. No customer photo, certification, urgency countdown, stock claim or health outcome is invented.

The previous contact form is replaced by direct order links to the confirmed destinations. No server, payment collection, new dependency or customer data storage is introduced. Static links and details work without JavaScript. WhatsApp links ask the customer to complete their PIN code; the maker confirms delivery and payment in the conversation. A clicked draft does not itself confirm an order.

## Validation and release

Checks cover pack prices, order destinations, email encoding, local assets and links, preserved ingredient references, metadata, mobile navigation, closed FAQs and operation without JavaScript. Browser order destinations are mocked; no real orders are sent. The existing CI rebuilds generated files and runs static and browser checks.

Review the pull request into `v2`; leave `main` untouched. The site is static and needs no migration. After merge and deployment, check both pack links, email, the review link and FAQs on a phone. Revert the change commit on `v2` to restore the prior layout if needed. Search Console remains the place to assess indexing and search performance; the layout makes no ranking guarantee.
