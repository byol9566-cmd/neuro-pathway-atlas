import { defineConfig } from 'vitest/config';

export default defineConfig({
  // relative asset URLs so the build works from any sub-path (GitHub Pages, a zip opened via a local server, ...)
  base: './',
  // content/*.json lives one level above the viewer
  server: { fs: { allow: ['..'] } },
  test: { include: ['tests/**/*.test.ts'] },
});
