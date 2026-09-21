import { defineConfig } from '@playwright/test';

export default defineConfig({
  testDir: 'e2e',
  timeout: 60_000,
  use: {
    baseURL: 'http://localhost:5199',
    viewport: { width: 1500, height: 900 },
    // calm mode: no intro sequence or drifting background, so states and screenshots are deterministic
    contextOptions: { reducedMotion: 'reduce' },
    // headless Chromium has no GPU by default; ANGLE's software path keeps WebGL available
    launchOptions: { args: ['--use-angle=swiftshader', '--enable-unsafe-swiftshader', '--ignore-gpu-blocklist'] },
  },
  webServer: { command: 'npx vite --port 5199 --strictPort', url: 'http://localhost:5199', reuseExistingServer: true },
});
