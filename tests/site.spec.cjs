const { test, expect } = require('@playwright/test');

for (const width of [375, 1440]) {
  for (const url of ['/', '/ingredients.html']) {
    test(`static content and icons at ${width}px: ${url}`, async ({ browser }) => {
      const context = await browser.newContext({ javaScriptEnabled: false, viewport: { width, height: 900 } });
      const page = await context.newPage();
      await page.goto(url);
      await page.evaluate(() => document.fonts.ready);
      if (url === '/') {
        await expect(page.locator('.category-card')).toHaveCount(6);
        await expect(page.locator('.pack-card')).toHaveCount(2);
        await expect(page.getByRole('link', { name: 'Order on WhatsApp: 500 g for ₹300' })).toBeVisible();
        await expect(page.getByRole('link', { name: 'Order on WhatsApp: 1 kg for ₹600' })).toBeVisible();
        await expect(page.locator('#faq details[open]')).toHaveCount(0);
        await page.locator('#faq summary').filter({ hasText: 'How can I pay?' }).click();
        await expect(page.getByText('Courier orders require UPI payment.', { exact: false })).toBeVisible();
        await page.locator('#faq summary').filter({ hasText: 'How can I pay?' }).click();
        await expect(page.locator('#faq details[open]')).toHaveCount(0);
      } else {
        await expect(page.locator('article.ingredient-detail')).toHaveCount(42);
        await expect(page.locator('.ingredient-detail').first()).toBeVisible();
      }
      await expect(page.locator('h1')).toBeVisible();
      expect(await page.evaluate(() => document.documentElement.scrollWidth <= innerWidth)).toBe(true);
      const iconSizes = await page.locator('.ingredient-icon').evaluateAll(nodes => nodes.map(n => {
        const b = n.getBBox(); return [b.width, b.height];
      }));
      expect(iconSizes.every(([w,h]) => w > 0 && h > 0)).toBe(true);
      for (const img of await page.locator('img').all()) {
        await img.scrollIntoViewIfNeeded();
        await expect.poll(() => img.evaluate(n => n.complete && n.naturalWidth > 0)).toBe(true);
      }
      if (width === 375 && url === '/') {
        await page.locator('.mobile-nav summary').click();
        await page.locator('.mobile-nav a[href="#ingredients"]').click();
        await expect(page).toHaveURL(/#ingredients$/);
        await page.locator('.mobile-nav summary').click();
      }
      await page.screenshot({path: `test-results/${width}-${url === '/' ? 'home' : 'ingredients'}.png`,fullPage:true});
      await context.close();
    });
  }
}

for (const [size, price] of [['500 g', '₹300'], ['1 kg', '₹600']]) {
  test(`order link opens the correct WhatsApp draft: ${size}`, async ({ context, page }) => {
    // No message is sent and no request reaches WhatsApp.
    await context.route('https://wa.me/**', route => route.fulfill({contentType:'text/html',body:'Order draft preview'}));
    await page.goto('/');
    const popupPromise = page.waitForEvent('popup');
    await page.getByRole('link', { name: `Order on WhatsApp: ${size} for ${price}` }).click();
    const popup = await popupPromise;
    await popup.waitForLoadState();
    const destination = new URL(popup.url());
    expect(destination.hostname).toBe('wa.me');
    expect(destination.pathname).toBe('/919148109589');
    expect(destination.searchParams.get('text')).toContain(`(${size}, ${price})`);
    await popup.close();
  });
}

test('email order link uses the confirmed address and readable draft', async ({ page }) => {
  await page.goto('/');
  const href = await page.getByRole('link', { name: 'Order by email', exact: true }).getAttribute('href');
  const destination = new URL(href);
  expect(destination.protocol).toBe('mailto:');
  expect(destination.pathname).toBe('mirthuposhan@gmail.com');
  expect(destination.searchParams.get('body')).toContain('\nDelivery PIN code:');
});

test('mobile menu closes after navigation and FAQs stay collapsed', async ({ page }) => {
  await page.setViewportSize({width:375,height:900});
  await page.goto('/');
  await page.locator('.mobile-nav summary').click();
  await page.locator('.mobile-nav a[href="#faq"]').click();
  await expect(page.locator('.mobile-nav')).not.toHaveAttribute('open');
  await expect(page.locator('#faq details[open]')).toHaveCount(0);
});

test('the existing process fragment opens the preparation details', async ({ page }) => {
  await page.goto('/#process');
  await expect(page.locator('#process')).toHaveAttribute('open');
  await expect(page.getByText('Sift through a sieve to remove coarse particles.', {exact:true})).toBeVisible();
});
