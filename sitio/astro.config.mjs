import { defineConfig } from 'astro/config';
export default defineConfig({
  site: process.env.SITE_URL ?? 'https://iglesias-ar.workers.dev',
  output: 'static',
  build: { format: 'directory' },
  trailingSlash: 'ignore',
});
