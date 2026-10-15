import { defineConfig } from 'astro/config';
export default defineConfig({
  site: process.env.SITE_URL ?? 'https://iglesias-latam.workers.dev',
  output: 'static',
  build: { format: 'directory' },
  trailingSlash: 'ignore',
});
