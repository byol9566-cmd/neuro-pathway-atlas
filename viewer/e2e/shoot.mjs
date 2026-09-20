// Ad-hoc screenshots: node e2e/shoot.mjs <outDir> '<json array of {name, mode, view?, wait?}>'
import { chromium } from '@playwright/test';

const [outDir, specJson] = process.argv.slice(2);
const specs = JSON.parse(specJson);
const browser = await chromium.launch({ args: ['--use-angle=swiftshader', '--enable-unsafe-swiftshader', '--ignore-gpu-blocklist'] });
const page = await browser.newPage({ viewport: { width: 1500, height: 900 } });
page.on('pageerror', (e) => console.error('pageerror:', e.message));
await page.goto(process.env.ATLAS_URL ?? 'http://localhost:5199/');
await page.waitForFunction(() => window.__atlas, null, { timeout: 30000 });
for (const s of specs) {
  await page.evaluate(({ mode, view }) => {
    window.__atlas.setMode(mode, { focus: true });
    if (view) window.__atlas.setView(view);
  }, s);
  await page.waitForTimeout(s.wait ?? 2500);
  await page.locator('#stage').screenshot({ path: `${outDir}/${s.name}.png` });
  console.log('shot', s.name);
}
await browser.close();
