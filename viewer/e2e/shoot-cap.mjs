// The slice laid on the 3D cut face while a pathway is shown: node e2e/shoot-cap.mjs <outDir>
import { chromium } from '@playwright/test';
const out = process.argv[2];
const browser = await chromium.launch({ args: ['--use-angle=metal', '--enable-gpu', '--ignore-gpu-blocklist'] });
const page = await browser.newPage({ viewport: { width: 1500, height: 900 } });
page.on('pageerror', (e) => console.error('pageerror:', e.message));
page.on('console', (m) => m.type() === 'error' && console.error('console:', m.text()));
await page.addInitScript(() => sessionStorage.setItem('atlas.intro', '1'));
await page.goto('http://localhost:5199/');
await page.waitForFunction(() => window.__atlas, null, { timeout: 30000 });
await page.waitForTimeout(2000);
await page.locator('[data-pathway="dcml"]').click();
await page.waitForTimeout(1500);
for (let i = 0; i < 3; i++) { await page.getByRole('button', { name: '다음 →' }).click(); await page.waitForTimeout(300); }
await page.locator('.section-toggle').click();
await page.waitForTimeout(1200);
await page.locator('#section-cut').check();
await page.evaluate(() => window.__atlas.setView('superior'));
await page.waitForTimeout(2500);
await page.screenshot({ path: `${out}/cap-1-top.png` });
await page.evaluate(() => window.__atlas.setView('oblique'));
await page.waitForTimeout(2000);
await page.screenshot({ path: `${out}/cap-2-home.png` });
console.log('ok');
await browser.close();
