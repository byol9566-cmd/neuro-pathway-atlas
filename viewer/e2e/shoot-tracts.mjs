// HCP1065 tract tubes and the pathways that now follow them: node e2e/shoot-tracts.mjs <outDir>
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
const unfold = async (btn) => {
  const group = btn.locator('xpath=ancestor::section[contains(@class, "group")]');
  if (await group.evaluate((g) => g.classList.contains('collapsed'))) await group.locator('.fold').click();
};
const pickStructure = async (id) => { const b = page.locator(`[data-structure="${id}"]`); await unfold(b); await b.click(); await page.waitForTimeout(2200); };
const openPathway = async (id) => { const b = page.locator(`[data-pathway="${id}"]`); await unfold(b); await b.click(); await page.waitForTimeout(2200); };
const next = async (n) => { for (let i = 0; i < n; i++) { await page.getByRole('button', { name: '다음 →' }).click(); await page.waitForTimeout(500); } await page.waitForTimeout(1800); };

let i = 1;
for (const id of ['tr-cst-cerebral', 'tr-cst-lateral', 'tr-medial-lemniscus', 'tr-optic-radiation', 'tr-arcuate']) {
  await pickStructure(id);
  await page.screenshot({ path: `${out}/tr-${i++}-${id}.png` });
  console.log(id, '|', (await page.locator('#detail').textContent()).replace(/\s+/g, ' ').slice(0, 220));
  await page.keyboard.press('Escape');
  await page.waitForTimeout(400);
}
await openPathway('corticospinal-lateral');
await page.screenshot({ path: `${out}/tr-${i++}-cst-step1.png` });
await next(2);
await page.screenshot({ path: `${out}/tr-${i++}-cst-step3.png` });
await page.keyboard.press('Escape');
await openPathway('dcml');
await next(3);
await page.screenshot({ path: `${out}/tr-${i++}-dcml-step4.png` });
await page.keyboard.press('Escape');
await openPathway('visual-nasal');
await next(3);
await page.screenshot({ path: `${out}/tr-${i++}-visual-nasal.png` });
await browser.close();
