// Frames of a click ripple on empty space, rendered on the real GPU: node e2e/shoot-ripple.mjs <outDir>
import { chromium } from '@playwright/test';

const out = process.argv[2];
const browser = await chromium.launch({ args: ['--use-angle=metal', '--enable-gpu', '--ignore-gpu-blocklist'] });
const page = await browser.newPage({ viewport: { width: 1500, height: 900 } });
page.on('pageerror', (e) => console.error('pageerror:', e.message));
page.on('console', (m) => ['error', 'warning'].includes(m.type()) && console.error(`${m.type()}:`, m.text()));
await page.goto(process.env.ATLAS_URL ?? 'http://localhost:5199/');
await page.waitForFunction(() => window.__atlas, null, { timeout: 30000 });
await page.waitForTimeout(5200); // entrance over, its own ripple gone
await page.screenshot({ path: `${out}/ripple-0-before.png` });
await page.mouse.click(1180, 640);
const t0 = Date.now();
for (const ms of [350, 1000, 1900, 3200]) {
  await page.waitForTimeout(Math.max(0, ms - (Date.now() - t0)));
  await page.screenshot({ path: `${out}/ripple-${String(ms).padStart(4, '0')}ms.png` });
}
await page.mouse.click(1100, 300);
await page.mouse.click(1300, 520);
await page.waitForTimeout(1300);
await page.screenshot({ path: `${out}/ripple-two-drops.png` });
console.log('stats:', await page.locator('#stats').textContent(), '| mode:', await page.evaluate(() => window.__atlas.mode.kind));
await browser.close();
