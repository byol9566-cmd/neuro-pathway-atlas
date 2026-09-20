import { expect, test, type Page } from '@playwright/test';

const SHOTS = process.env.SHOTS_DIR;

async function ready(page: Page) {
  const errors: string[] = [];
  page.on('pageerror', (e) => errors.push(e.message));
  page.on('console', (m) => m.type() === 'error' && errors.push(m.text()));
  await page.goto('/');
  await expect(page.locator('#loading')).toBeHidden({ timeout: 30_000 });
  return errors;
}

const states = (page: Page) => page.evaluate(() => (window as any).__atlas.states() as Record<string, string>);
const settle = (page: Page) => page.waitForTimeout(1500); // camera fly + route reveal
const shot = async (page: Page, name: string) => {
  if (SHOTS) await page.screenshot({ path: `${SHOTS}/${name}.png` });
};

test('loads every mesh and starts in explore mode', async ({ page }) => {
  const errors = await ready(page);
  const meshCount = await page.evaluate(() => (window as any).__atlas.meshCount);
  expect(meshCount).toBeGreaterThan(90);
  const s = await states(page);
  expect(s['shell-cerebrum.L']).toBe('ghost');
  expect(s['thal-vpl.L']).toBe('normal');
  await settle(page);
  await shot(page, '01-explore');
  expect(errors).toEqual([]);
});

test('DCML pathway highlights the contralateral chain and flips with the origin side', async ({ page }) => {
  await ready(page);
  await page.locator('[data-pathway="dcml"]').click();
  let s = await states(page);
  expect(s['bs-gracile.R']).toBe('involved'); // default origin: right body
  expect(s['tr-medial-lemniscus.L']).toBe('involved');
  expect(s['thal-vpl.L']).toBe('involved');
  expect(s['thal-vpl.R']).toBe('ghost');
  expect(s['bg-putamen.L']).toBe('ghost');

  await page.getByRole('button', { name: '다음 →' }).click();
  s = await states(page);
  expect(s['bs-gracile.R']).toBe('active');
  expect(s['bs-cuneate.R']).toBe('active');
  await settle(page);
  await shot(page, '02-dcml-step2');

  await page.getByRole('button', { name: '다음 →' }).click();
  await page.getByRole('button', { name: '다음 →' }).click();
  await page.getByRole('button', { name: '다음 →' }).click();
  await expect(page.getByRole('button', { name: '다음 →' })).toBeDisabled();
  await settle(page);
  await page.waitForTimeout(1500);
  await shot(page, '03-dcml-final');

  await page.locator('[data-origin="L"]').click();
  s = await states(page);
  expect(s['ctx-postcentral.R']).toBe('active');
  expect(s['ctx-postcentral.L']).toBe('ghost');
  expect(s['bs-gracile.L']).toBe('involved');
});

test('selecting a structure isolates it; Escape returns to explore', async ({ page }) => {
  await ready(page);
  await page.locator('#search').fill('VPL');
  await expect(page.locator('.structure:visible')).toHaveCount(1);
  await page.locator('[data-structure="thal-vpl"]').click();
  const s = await states(page);
  expect(s['thal-vpl.L']).toBe('active');
  expect(s['thal-vpl.R']).toBe('active');
  expect(s['thal-vpm.L']).toBe('ghost');
  await expect(page.locator('#detail h2')).toContainText('VPL');
  await settle(page);
  await shot(page, '04-structure-vpl');
  await page.keyboard.press('Escape');
  expect((await states(page))['thal-vpm.L']).toBe('normal');
});

test('remaining pathways render', async ({ page }) => {
  const errors = await ready(page);
  for (const [id, name] of [['papez', '05-papez'], ['hvor', '06-hvor']] as const) {
    await page.locator(`[data-pathway="${id}"]`).click();
    const steps = await page.locator('.steps li').count();
    for (let i = 1; i < steps; i++) await page.getByRole('button', { name: '다음 →' }).click();
    await settle(page);
    await page.waitForTimeout(2000);
    await shot(page, name);
  }
  expect(errors).toEqual([]);
});

test('clicking a mesh in the 3D view selects its structure', async ({ page }) => {
  await ready(page);
  await settle(page);
  const box = (await page.locator('#canvas').boundingBox())!;
  await page.mouse.move(box.x + box.width / 2, box.y + box.height / 2);
  await expect(page.locator('#tooltip')).toBeVisible();
  const hovered = await page.locator('#tooltip').textContent();
  await page.mouse.click(box.x + box.width / 2, box.y + box.height / 2);
  const mode = await page.evaluate(() => (window as any).__atlas.mode);
  expect(mode.kind).toBe('structure');
  await expect(page.locator('#detail h2')).toHaveText(hovered!.split(' · ')[0]);
});

test('section panel shows the atlas labels at the chosen level and follows the selection', async ({ page }) => {
  const errors = await ready(page);
  await page.locator('.section-toggle').click();
  await expect(page.locator('#section')).toBeVisible();

  // red nucleus centroid in the atlas: (-5.4, -18.4, -11.6) mm, label 385
  await page.evaluate(() => (window as any).__atlas.section.setZ(-11.6));
  await expect(page.locator('.section-readout')).toHaveText('z = -11.4 mm'); // nearest 0.4 mm slice
  await expect.poll(() => page.evaluate(() => (window as any).__atlas.section.labelAtMm(-5.4, -18.4))).toBe(385);
  // the right side is the mirror image
  expect(await page.evaluate(() => (window as any).__atlas.section.labelAtMm(5.4, -18.4))).toBe(385);

  // selecting a structure moves the section to its level
  await page.locator('[data-structure="bs-facial"]').click();
  await expect.poll(() => page.evaluate(() => (window as any).__atlas.section.z)).toBeLessThan(-40);
  await settle(page);
  await shot(page, '07-section-facial');

  await page.locator('#section-cut').check();
  await settle(page);
  await shot(page, '08-section-cut');
  expect(errors).toEqual([]);
});
