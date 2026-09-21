// The mist sea at rest, while the pointer crosses it, and after a click: node e2e/shoot-sea.mjs <outDir>
import { chromium } from '@playwright/test';

const out = process.argv[2];
const browser = await chromium.launch({ args: ['--use-angle=metal', '--enable-gpu', '--ignore-gpu-blocklist'] });
const page = await browser.newPage({ viewport: { width: 1500, height: 900 } });
page.on('pageerror', (e) => console.error('pageerror:', e.message));
page.on('console', (m) => ['error', 'warning'].includes(m.type()) && console.error(`${m.type()}:`, m.text().slice(0, 300)));
await page.addInitScript(() => sessionStorage.setItem('atlas.intro', '1')); // returning visitor: no opening film
await page.goto(process.env.ATLAS_URL ?? 'http://localhost:5199/');
await page.waitForFunction(() => window.__atlas, null, { timeout: 30000 });
await page.waitForTimeout(5500);
await page.screenshot({ path: `${out}/sea-0-rest.png` });
await page.mouse.move(520, 700);
await page.mouse.move(1150, 560, { steps: 40 });
await page.waitForTimeout(500);
await page.screenshot({ path: `${out}/sea-1-after-hover.png` });
await page.mouse.click(1200, 700);
await page.waitForTimeout(900);
await page.screenshot({ path: `${out}/sea-2-click-0900ms.png` });
await page.waitForTimeout(2600);
await page.screenshot({ path: `${out}/sea-3-click-3500ms.png` });
console.log('stats:', await page.locator('#stats').textContent());
await browser.close();
