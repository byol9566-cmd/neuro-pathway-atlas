// Visible-Human-derived structures: eyeballs, retina/cornea cut from them, pituitary lobes, spinal cord: node e2e/shoot-vhp.mjs <outDir>
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
const pick = async (id) => {
  const btn = page.locator(`[data-structure="${id}"]`);
  const group = btn.locator('xpath=ancestor::section[contains(@class, "group")]');
  if (await group.evaluate((g) => g.classList.contains('collapsed'))) await group.locator('.fold').click();
  await btn.click();
  await page.waitForTimeout(2500);
};
let i = 1;
for (const id of ['so-eyeball', 'so-retina', 'so-cornea', 'so-nasal-retina', 'end-ant-pituitary', 'end-post-pituitary', 'sp-cord']) {
  await pick(id);
  await page.screenshot({ path: `${out}/vhp-${i++}-${id}.png` });
  console.log(id, '|', (await page.locator('#detail').textContent()).replace(/\s+/g, ' ').slice(0, 300));
  await page.keyboard.press('Escape');
  await page.waitForTimeout(400);
}
await browser.close();
