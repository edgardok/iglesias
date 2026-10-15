import { defineConfig } from 'astro/config';
export default defineConfig({
  site: 'https://iglesias-ar.pages.dev',
  output: 'static',
  build: { format: 'directory' },
  trailingSlash: 'ignore',
});
