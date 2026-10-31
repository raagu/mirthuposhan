const { test, expect } = require('@playwright/test');
const http = require('node:http');
const fs = require('node:fs');
const path = require('node:path');

const root = path.resolve(__dirname, '..');
const mime = { '.css': 'text/css', '.js': 'application/javascript', '.html': 'text/html',
  '.svg': 'image/svg+xml', '.woff2': 'font/woff2', '.webp': 'image/webp', '.png': 'image/png' };

for (const width of [375, 1440]) {
  test(`returning visitor gets current styles and script at ${width}px`, async ({ browser }) => {
    // Use real browser HTTP caching. Playwright request routing disables the cache.
    let previousRelease = true;
    const requests = { '/assets/site.css': 0, '/assets/site.js': 0 };
    const server = http.createServer((req, res) => {
      const pathname = new URL(req.url, 'http://localhost').pathname;
      if (pathname === '/previous-release.html') {
        res.writeHead(200, { 'Content-Type': 'text/html', 'Cache-Control': 'no-store' });
        return res.end('<!doctype html><link rel="stylesheet" href="/assets/site.css">' +
          '<script src="/assets/site.js" defer></script><p>Previous release</p>');
      }
      const file = path.resolve(root, '.' + (pathname === '/' ? '/index.html' : pathname));
      if (!file.startsWith(root + path.sep) || !fs.existsSync(file) || !fs.statSync(file).isFile()) {
        res.writeHead(404);
        return res.end();
      }
      if (Object.hasOwn(requests, pathname)) requests[pathname]++;
      res.writeHead(200, {
        'Content-Type': mime[path.extname(file)] || 'application/octet-stream',
        'Cache-Control': pathname === '/' || pathname.endsWith('.html') ? 'no-store' : 'max-age=600',
      });
      if (previousRelease && pathname === '/assets/site.css') {
        // Previous styles have no rules for the redesigned header and pack grid.
        return res.end('body { font-family: serif; }');
      }
      if (previousRelease && pathname === '/assets/site.js') {
        return res.end('window.previousSiteScript = true;');
      }
      res.end(fs.readFileSync(file));
    });
    await new Promise((resolve, reject) => {
      server.once('error', reject);
      server.listen(0, '127.0.0.1', resolve);
    });
    const origin = `http://127.0.0.1:${server.address().port}`;
    const context = await browser.newContext({ viewport: { width, height: 900 } });
    try {
      const page = await context.newPage();
      await page.goto(origin + '/previous-release.html');
      await expect.poll(() => page.evaluate(() => window.previousSiteScript)).toBe(true);
      await page.goto(origin + '/previous-release.html?again');
      await expect.poll(() => page.evaluate(() => window.previousSiteScript)).toBe(true);
      expect(requests).toEqual({ '/assets/site.css': 1, '/assets/site.js': 1 });

      previousRelease = false;
      await page.goto(origin + '/');
      await expect(page.locator('.home-header')).toHaveCSS('position', 'fixed');
      await expect(page.locator('.pack-grid')).toHaveCSS('display', 'grid');
      expect(await page.evaluate(() => window.previousSiteScript)).toBeUndefined();
      expect(requests).toEqual({ '/assets/site.css': 1, '/assets/site.js': 1 });
      expect(await page.evaluate(() => document.documentElement.scrollWidth <= innerWidth)).toBe(true);
      if (width === 375) {
        await page.locator('.mobile-nav summary').click();
        await page.locator('.mobile-nav a[href="#faq"]').click();
        await expect(page.locator('.mobile-nav')).not.toHaveAttribute('open');
      }
    } finally {
      await context.close();
      await new Promise(resolve => server.close(resolve));
    }
  });
}
