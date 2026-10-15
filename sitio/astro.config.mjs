import { defineConfig } from 'astro/config';
import cloudflare from '@astrojs/cloudflare';
export default defineConfig({
  site: process.env.SITE_URL ?? 'https://iglesias.edgardo-krause.workers.dev',
  output: 'static',            // todo estático salvo las páginas con `export const prerender = false` (fichas, localidades, API), que corren en el Worker y leen D1
  adapter: cloudflare({ imageService: 'passthrough' }),
  build: { format: 'directory' },
  trailingSlash: 'ignore',
});
