// The 247-pathway sidebar, a pathway that lights up new structures, and a text-only mechanism: node e2e/shoot-paths.mjs <outDir>
import { chromium } from '@playwright/test';
const out = process.argv[2];
const browser = await chromium.launch({ args: ['--use-angle=metal', '--enable-gpu', '--ignore-gpu-blocklist'] });
const page = await browser.newPage({ viewport: { width: 1500, height: 900 } });
page.on('pageerror', (e) => console.error('pageerror:', e.message));
page.on('console', (m) => m.type() === 'error' && console.error('console:', m.text()));
await page.addInitScript(() => sessionStorage.setItem('atlas.intro', '1'));
await page.goto('http://localhost:5199/');
await page.waitForFunction(() => window.__atlas, null, { timeout: 30000 });
await page.waitForTimeout(2500);
await page.screenshot({ path: `${out}/p-1-sidebar.png` });
const open = async (id) => {
  const btn = page.locator(`[data-pathway="${id}"]`);
  const group = btn.locator('xpath=ancestor::section[contains(@class, "group")]');
  if (await group.evaluate((g) => g.classList.contains('collapsed'))) await group.locator('.fold').click();
  await btn.click();
  await page.waitForTimeout(2500);
};
await open('pupillary-light-reflex');
for (let i = 0; i < 2; i++) { await page.getByRole('button', { name: '다음 →' }).click(); await page.waitForTimeout(400); }
await page.waitForTimeout(1800);
await page.screenshot({ path: `${out}/p-2-pupillary.png` });
await page.keyboard.press('Escape');
await open('autonomic-micturition');
await page.screenshot({ path: `${out}/p-3-micturition.png` });
await page.keyboard.press('Escape');
await open('retinal-off');
await page.screenshot({ path: `${out}/p-4-text-only.png` });
console.log('stats:', await page.locator('#stats').textContent(), '| pathway buttons:', await page.locator('[data-pathway]').count());
await browser.close();
