// Parametric models (labyrinth, ganglia, cord columns) and nuclei rebuilt from probability maps: node e2e/shoot-models.mjs <outDir>
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
  await page.waitForTimeout(2400);
};
let i = 1;
for (const id of ['so-cochlea', 'so-horizontal-canal', 'pn-spiral-ganglion', 'pn-trigeminal-ganglion', 'pn-superior-cervical', 'sp-iml', 'sp-cord-extension', 'bs-abducens', 'bs-oculomotor', 'end-pineal', 'bs-solitary']) {
  await pick(id);
  await page.screenshot({ path: `${out}/md-${i++}-${id}.png` });
  console.log(id, '|', (await page.locator('#detail').textContent()).replace(/\s+/g, ' ').slice(0, 200));
  await page.keyboard.press('Escape');
  await page.waitForTimeout(400);
}
await browser.close();
