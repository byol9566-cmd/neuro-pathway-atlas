// Frames of the opening film handing over to the scene: node e2e/shoot-film.mjs <outDir> [webkit|chromium]
// The film is H.264, so either engine plays it.
import { chromium, webkit } from '@playwright/test';

const out = process.argv[2];
const engine = process.argv[3] ?? 'webkit';
const browser = engine === 'webkit' ? await webkit.launch() : await chromium.launch({ args: ['--use-angle=metal', '--enable-gpu', '--ignore-gpu-blocklist'] });
const page = await browser.newPage({ viewport: { width: 1500, height: 900 } });
page.on('pageerror', (e) => console.error('pageerror:', e.message));
page.on('console', (m) => m.type() === 'error' && console.error('console:', m.text()));
await page.goto(process.env.ATLAS_URL ?? 'http://localhost:5199/');
const t0 = Date.now();
for (const ms of [1500, 4000, 7000, 9000, 10000, 11000, 12500, 15000]) {
  await page.waitForTimeout(Math.max(0, ms - (Date.now() - t0)));
  const state = await page.evaluate(() => {
    const v = document.querySelector('#intro-video');
    const l = document.querySelector('#loading');
    return { t: +v.currentTime.toFixed(2), film: l.classList.contains('with-film'), leaving: l.classList.contains('leaving'), hidden: l.hidden, error: v.error?.code ?? null };
  });
  console.log(ms, JSON.stringify(state));
  await page.screenshot({ path: `${out}/film-${engine}-${String(ms).padStart(5, '0')}ms.png` });
}
await browser.close();
