// Ad-hoc screenshots of the 2D section panel: node e2e/shoot-section.mjs <outDir>
import { chromium } from '@playwright/test';

const out = process.argv[2];
const browser = await chromium.launch({ args: ['--use-angle=swiftshader', '--enable-unsafe-swiftshader', '--ignore-gpu-blocklist'] });
const page = await browser.newPage({ viewport: { width: 1500, height: 900 } });
page.on('pageerror', (e) => console.error('pageerror:', e.message));
await page.goto(process.env.ATLAS_URL ?? 'http://localhost:5199/');
await page.waitForFunction(() => window.__atlas, null, { timeout: 30000 });
await page.locator('.section-toggle').click();
await page.evaluate(() => window.__atlas.section.setZ(-40));
await page.locator('#section button[title="뇌줄기 확대"]').click();
await page.waitForTimeout(2500);
await page.locator('#section').screenshot({ path: `${out}/sec-explore-pons.png` });
await page.locator('[data-pathway="dcml"]').click();
await page.getByRole('button', { name: '다음 →' }).click();
await page.waitForTimeout(2500);
await page.locator('#section').screenshot({ path: `${out}/sec-dcml-step2.png` });
await browser.close();
