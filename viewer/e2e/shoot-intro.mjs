// Frames of the entrance sequence and the settled UI, rendered on the real GPU:
//   node e2e/shoot-intro.mjs <outDir>
import { chromium } from '@playwright/test';

const out = process.argv[2];
const browser = await chromium.launch({ args: ['--use-angle=metal', '--enable-gpu', '--ignore-gpu-blocklist'] });
const page = await browser.newPage({ viewport: { width: 1500, height: 900 } });
page.on('pageerror', (e) => console.error('pageerror:', e.message));
page.on('console', (m) => m.type() === 'error' && console.error('console:', m.text()));
await page.goto(process.env.ATLAS_URL ?? 'http://localhost:5199/');
await page.screenshot({ path: `${out}/intro-0-loading.png` });
await page.waitForFunction(() => window.__atlas, null, { timeout: 30000 });
const t0 = Date.now();
for (const ms of [500, 1300, 2100, 2900, 4300]) {
  await page.waitForTimeout(Math.max(0, ms - (Date.now() - t0)));
  await page.screenshot({ path: `${out}/intro-${String(ms).padStart(4, '0')}ms.png` });
}
await page.locator('[data-pathway="dcml"]').click();
for (let i = 0; i < 3; i++) await page.getByRole('button', { name: '다음 →' }).click();
await page.waitForTimeout(2600);
await page.screenshot({ path: `${out}/ui-pathway.png` });
await page.keyboard.press('Escape');
await page.locator('[data-structure="thal-vpl"]').click();
await page.locator('.section-toggle').click();
await page.waitForTimeout(2600);
await page.screenshot({ path: `${out}/ui-structure-section.png` });
console.log('fps:', await page.locator('#stats').textContent());
await browser.close();
