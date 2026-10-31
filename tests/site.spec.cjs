const { test, expect } = require('@playwright/test');

for (const width of [375, 1440]) {
  for (const url of ['/', '/ingredients.html']) {
    test(`static content and icons at ${width}px: ${url}`, async ({ browser }) => {
      const context = await browser.newContext({ javaScriptEnabled: false, viewport: { width, height: 900 } });
      const page = await context.newPage();
      await page.goto(url);
      await expect(page.locator('article.ingredient-detail')).toHaveCount(42);
      await expect(page.locator('h1')).toBeVisible();
      await expect(page.locator('.ingredient-detail').first()).toBeVisible();
      expect(await page.evaluate(() => document.documentElement.scrollWidth <= innerWidth)).toBe(true);
      const iconSizes = await page.locator('.ingredient-icon').evaluateAll(nodes => nodes.map(n => {
        const b = n.getBBox(); return [b.width, b.height];
      }));
      expect(iconSizes.every(([w,h]) => w > 0 && h > 0)).toBe(true);
      const images = await page.locator('img').evaluateAll(nodes => nodes.filter(n => n.loading !== 'lazy').map(n => n.complete && n.naturalWidth > 0));
      expect(images.every(Boolean)).toBe(true);
      if (width === 375 && url === '/') {
        await page.locator('.mobile-nav summary').click();
        await expect(page.locator('.mobile-nav a[href="#ingredients"]')).toBeVisible();
        await page.locator('.mobile-nav a[href="#ingredients"]').click();
        await expect(page).toHaveURL(/#ingredients$/);
      }
      await page.screenshot({path: `test-results/${width}-${url === '/' ? 'home' : 'ingredients'}.png`,fullPage:true});
      await context.close();
    });
  }
}

for (const outcome of ['success', 'error', 'malformed', 'network', 'timeout']) {
  test(`contact form ${outcome} preserves correct state`, async ({ page }) => {
    const errors = [];
    page.on('pageerror', e => errors.push(e.message));
    // No real enquiry is sent; all submissions are intercepted.
    if (outcome === 'timeout') await page.clock.install();
    await page.route('https://api.web3forms.com/submit', async route => {
      if (outcome === 'network') return route.abort();
      if (outcome === 'timeout') return;
      return route.fulfill({status: outcome === 'error' ? 500 : 200,
        contentType: 'application/json',body: outcome === 'malformed' ? '{' : JSON.stringify({success:outcome === 'success'})});
    });
    await page.goto('/');
    await page.getByLabel('Full Name').fill('Test Customer');
    await page.getByLabel('Email Address').fill('customer@example.com');
    await page.getByLabel('Phone Number').fill('9000000000');
    await page.getByLabel('Message', {exact:true}).fill('Test enquiry');
    await page.getByRole('button',{name:'Send Message'}).click();
    if (outcome === 'timeout') await page.clock.fastForward(16000);
    const status = page.getByRole('status');
    await expect(status).toContainText(outcome === 'success' ? 'Message sent.' : 'could not be confirmed');
    await expect(page.getByRole('button',{name:'Send Message'})).toBeEnabled();
    await expect(page.getByLabel('Full Name')).toHaveValue(outcome === 'success' ? '' : 'Test Customer');
    expect(errors).toEqual([]);
  });
}
