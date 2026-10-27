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
/** Click a structure in the sidebar; long groups start folded, so unfold its group first the way a user would. */
const pickStructure = async (page: Page, id: string) => {
  const btn = page.locator(`[data-structure="${id}"]`);
  const group = btn.locator('xpath=ancestor::section[contains(@class, "group")]');
  if (await group.evaluate((g) => g.classList.contains('collapsed'))) await group.locator('.fold').click();
  await btn.click();
};
const pickPathway = async (page: Page, id: string) => {
  const btn = page.locator(`[data-pathway="${id}"]`);
  const group = btn.locator('xpath=ancestor::section[contains(@class, "group")]');
  if (await group.evaluate((g) => g.classList.contains('collapsed'))) await group.locator('.fold').click();
  await btn.click();
};
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
  const errors = await ready(page);
  await pickPathway(page, 'dcml');
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
  expect(errors).toEqual([]);
});

test('selecting a structure isolates it; Escape returns to explore', async ({ page }) => {
  const errors = await ready(page);
  await page.locator('#search').fill('배쪽뒤가쪽');  // 'VPL' alone also matches the superior thalamic radiation
  await expect(page.locator('.structure:visible')).toHaveCount(1);
  await pickStructure(page, 'thal-vpl');
  const s = await states(page);
  expect(s['thal-vpl.L']).toBe('active');
  expect(s['thal-vpl.R']).toBe('active');
  expect(s['thal-vpm.L']).toBe('ghost');
  await expect(page.locator('#detail h2')).toContainText('VPL');
  await settle(page);
  await shot(page, '04-structure-vpl');
  await page.keyboard.press('Escape');
  expect((await states(page))['thal-vpm.L']).toBe('normal');
  expect(errors).toEqual([]);
});

test('remaining pathways render', async ({ page }) => {
  const errors = await ready(page);
  for (const [id, name] of [['papez', '05-papez'], ['hvor', '06-hvor']] as const) {
    await pickPathway(page, id);
    const steps = await page.locator('.steps li').count();
    for (let i = 1; i < steps; i++) await page.getByRole('button', { name: '다음 →' }).click();
    await settle(page);
    await page.waitForTimeout(2000);
    await shot(page, name);
  }
  expect(errors).toEqual([]);
});

test('every pathway opens and steps through without an error', async ({ page }) => {
  test.setTimeout(180_000);
  const errors = await ready(page);
  const ids = await page.locator('[data-pathway]').evaluateAll((els) => els.map((e) => (e as HTMLElement).dataset.pathway!));
  expect(ids.length).toBeGreaterThan(200);
  // every step of every pathway, alternating origin sides, in batches: under software WebGL the page renders
  // a frame (over a second with a new route) between any two calls, so the work stays inside the page and
  // only the end of each batch lets a frame through to exercise the per-frame code
  for (let i = 0; i < ids.length; i += 25) {
    const failed = await page.evaluate(async (batch) => {
      const atlas = (window as any).__atlas;
      const failed: string[] = [];
      for (const pathwayId of batch) {
        atlas.setMode({ kind: 'pathway', pathwayId, origin: 'R', step: 0, playing: false });
        const steps = document.querySelectorAll('#detail .steps li').length;
        if (!steps) failed.push(`${pathwayId}: no steps rendered`);
        for (let step = 0; step < steps; step++) {
          atlas.setMode({ kind: 'pathway', pathwayId, origin: step % 2 ? 'L' : 'R', step, playing: false });
          if (atlas.mode.step !== step || !document.querySelector('#detail .steps li.on')) failed.push(`${pathwayId}: step ${step} did not render`);
        }
      }
      await new Promise(requestAnimationFrame);
      return failed;
    }, ids.slice(i, i + 25));
    expect(failed).toEqual([]);
  }
  await page.evaluate(() => (window as any).__atlas.setMode({ kind: 'explore' }));
  expect(errors).toEqual([]);
});

test('clicking a mesh in the 3D view selects its structure', async ({ page }) => {
  const errors = await ready(page);
  await settle(page);
  const box = (await page.locator('#canvas').boundingBox())!;
  await page.mouse.move(box.x + box.width / 2, box.y + box.height / 2);
  await expect(page.locator('#tooltip')).toBeVisible();
  const hovered = await page.locator('#tooltip').textContent();
  await page.mouse.click(box.x + box.width / 2, box.y + box.height / 2);
  const mode = await page.evaluate(() => (window as any).__atlas.mode);
  expect(mode.kind).toBe('structure');
  await expect(page.locator('#detail h2')).toHaveText(hovered!.split(' · ')[0]);

  // and the panel's × really is on top and takes the click (a real pointer click, not a dispatched one)
  const close = (await page.locator('#detail .close').boundingBox())!;
  await page.mouse.click(close.x + close.width / 2, close.y + close.height / 2);
  expect(await page.evaluate(() => (window as any).__atlas.mode.kind)).toBe('explore');
  await expect(page.locator('#detail')).toBeHidden();
  expect(errors).toEqual([]);
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
  await pickStructure(page, 'bs-facial');
  await expect.poll(() => page.evaluate(() => (window as any).__atlas.section.z)).toBeLessThan(-40);
  await settle(page);
  await shot(page, '07-section-facial');

  await page.locator('#section-cut').check();
  await settle(page);
  await shot(page, '08-section-cut');
  expect(errors).toEqual([]);
});

type Sea = { goal: number; level: number; rest: number; bodyRevealed: boolean };
const sea = (page: Page) => page.evaluate(() => (window as any).__atlas.sea() as Sea);
const mode = (page: Page) => page.evaluate(() => (window as any).__atlas.mode as { kind: string; step: number; playing: boolean });

test('전신 and 자유 시점 toggle (aria-pressed), the mist follows the focus, and 초기화 resets both', async ({ page }) => {
  const errors = await ready(page);
  const body = page.getByRole('button', { name: '전신' });
  const free = page.getByRole('button', { name: '자유 시점' });
  await body.click();
  await expect(body).toHaveAttribute('aria-pressed', 'true');
  expect((await sea(page)).bodyRevealed).toBe(true);
  await expect.poll(async () => { const s = await sea(page); return s.level < s.rest - 500; }).toBe(true); // under the feet
  await free.click();
  await expect(free).toHaveAttribute('aria-pressed', 'true');
  expect(await page.evaluate(() => (window as any).__atlas.freeCamera())).toBe(true);

  await page.getByRole('button', { name: '초기화' }).click();
  await expect(body).toHaveAttribute('aria-pressed', 'false');
  await expect(free).toHaveAttribute('aria-pressed', 'false');
  expect(await page.evaluate(() => (window as any).__atlas.freeCamera())).toBe(false);
  let s = await sea(page);
  expect(s.bodyRevealed).toBe(false);
  expect(s.goal).toBe(s.rest);

  // a pathway reaching down the cord sinks the mist below it; leaving it brings the mist back up
  await pickPathway(page, 'spinothalamic-lateral');
  s = await sea(page);
  expect(s.goal).toBeLessThan(s.rest);
  await page.keyboard.press('Escape');
  s = await sea(page);
  expect(s.goal).toBe(s.rest);
  expect(errors).toEqual([]);
});

test('keyboard: Enter on a focused 다음 steps and keeps the focus; Space on a focused button does not play', async ({ page }) => {
  const errors = await ready(page);
  await pickPathway(page, 'dcml');
  const next = page.getByRole('button', { name: '다음 →' });
  await page.getByRole('button', { name: '재생' }).focus();
  await page.keyboard.press('Tab'); // 재생 → 다음
  await expect(next).toBeFocused();
  for (let i = 0; i < 3; i++) await page.keyboard.press('Enter');
  expect((await mode(page)).step).toBe(3);
  await expect(next).toBeFocused();

  await page.getByRole('button', { name: '← 이전' }).focus();
  await page.keyboard.press(' ');
  const m = await mode(page);
  expect(m.step).toBe(2); // Space pressed 이전…
  expect(m.playing).toBe(false); // …and did not also start playback
  // arrows still step from a focused button
  await page.keyboard.press('ArrowRight');
  expect((await mode(page)).step).toBe(3);
  expect(errors).toEqual([]);
});

test('the circuit box stays open or shut across steps and pathways, as the reader left it', async ({ page }) => {
  const errors = await ready(page);
  await pickPathway(page, 'dcml');
  const box = page.locator('#detail details.circuit-box');
  const wasOpen = await box.evaluate((d) => (d as HTMLDetailsElement).open);
  await box.locator('summary').click();
  const open = !wasOpen;
  await box.evaluate((d) => ((d as any).marked = true)); // the same element must survive a step change
  await page.getByRole('button', { name: '다음 →' }).click();
  await page.getByRole('button', { name: '다음 →' }).click();
  expect(await box.evaluate((d) => [(d as HTMLDetailsElement).open, (d as any).marked])).toEqual([open, true]);
  await expect(page.locator('#detail .circuit-node.on')).toHaveText(/^3/);

  await pickPathway(page, 'papez'); // another pathway remembers the choice too
  expect(await box.evaluate((d) => (d as HTMLDetailsElement).open)).toBe(open);
  expect(errors).toEqual([]);
});

test.describe('phone layout', () => {
  test.use({ viewport: { width: 390, height: 844 }, hasTouch: true });

  test('nothing scrolls but the docked panel, and the section sheet leaves the brain in view', async ({ page }) => {
    const errors = await ready(page);
    const fits = () => page.evaluate(() => document.documentElement.scrollHeight <= innerHeight && document.documentElement.scrollWidth <= innerWidth);
    expect(await fits()).toBe(true);

    // choosing a pathway swaps the lists for its description, right under the scene
    await pickPathway(page, 'dcml');
    await settle(page);
    await expect(page.locator('#sidebar')).toBeHidden();
    await expect(page.locator('#detail h2')).toBeInViewport();
    expect(await fits()).toBe(true);

    // the section takes the lower part of the scene; the panel folds away and the brain is framed above the sheet
    await page.locator('.section-toggle').tap();
    await settle(page);
    const sheet = (await page.locator('#section').boundingBox())!;
    const framing = await page.evaluate(() => (window as any).__atlas.framing() as { x: number; y: number; scale: number });
    const stageHeight = await page.evaluate(() => document.querySelector('#stage')!.clientHeight);
    expect(framing.y * stageHeight).toBeLessThan(sheet.y);
    expect(framing.scale).toBeLessThan(1);
    await shot(page, 'phone-section');

    await page.locator('#dock-toggle').tap();
    await expect(page.locator('#detail h2')).toBeInViewport();
    expect(errors).toEqual([]);
  });

  test('the toolbar wraps instead of overflowing, every button on screen and finger-sized', async ({ page }) => {
    const errors = await ready(page);
    const overflow = await page.locator('#toolbar').evaluate((t) => t.scrollWidth - t.clientWidth);
    expect(overflow).toBeLessThanOrEqual(0);
    const coarse = await page.evaluate(() => matchMedia('(pointer: coarse)').matches);
    const buttons = page.locator('#toolbar button');
    expect(await buttons.count()).toBeGreaterThanOrEqual(11);
    for (const b of await buttons.all()) {
      await expect(b).toBeInViewport({ ratio: 1 });
      expect((await b.boundingBox())!.height).toBeGreaterThanOrEqual(coarse ? 44 : 40);
    }
    // the docked sheet leaves most of the screen to the scene
    const sheet = (await page.locator('#sidebar').boundingBox())!;
    expect(sheet.height).toBeLessThan(844 * 0.34);
    expect(errors).toEqual([]);
  });

});
