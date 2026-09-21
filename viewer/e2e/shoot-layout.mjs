// The section window beside the brain — docked, next to the detail panel, and after a drag: node e2e/shoot-layout.mjs <outDir>
import { chromium } from '@playwright/test';

const out = process.argv[2];
const browser = await chromium.launch({ args: ['--use-angle=metal', '--enable-gpu', '--ignore-gpu-blocklist'] });
const page = await browser.newPage({ viewport: { width: 1500, height: 900 } });
page.on('pageerror', (e) => console.error('pageerror:', e.message));
page.on('console', (m) => m.type() === 'error' && console.error('console:', m.text()));
await page.addInitScript(() => sessionStorage.setItem('atlas.intro', '1'));
await page.goto(process.env.ATLAS_URL ?? 'http://localhost:5199/');
await page.waitForFunction(() => window.__atlas, null, { timeout: 30000 });
await page.waitForTimeout(2500);
await page.locator('.section-toggle').click();
await page.waitForTimeout(1500);
await page.screenshot({ path: `${out}/layout-1-section.png` });
await page.locator('[data-pathway="dcml"]').click();
await page.waitForTimeout(2500);
await page.screenshot({ path: `${out}/layout-2-section-pathway.png` });
const header = await page.locator('.section-header strong').boundingBox();
await page.mouse.move(header.x + 10, header.y + 6);
await page.mouse.down();
await page.mouse.move(420, 300, { steps: 12 });
await page.mouse.up();
await page.waitForTimeout(1500);
await page.screenshot({ path: `${out}/layout-3-dragged.png` });
console.log('section box:', JSON.stringify(await page.locator('#section').boundingBox()));
await browser.close();
