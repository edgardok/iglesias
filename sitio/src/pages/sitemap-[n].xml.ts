import { iglesias, urlIglesia } from '../lib/datos';
import { esDelgada } from '../lib/texto';
export const indexables = iglesias.filter(i => !esDelgada(i));
export const TAM = 10000;
export function getStaticPaths() { return Array.from({ length: Math.ceil(indexables.length / TAM) }, (_, n) => ({ params: { n: String(n) } })); }
export const GET = ({ params, site }: { params: { n: string }; site: URL }) => {
  const n = Number(params.n);
  const urls = indexables.slice(n * TAM, (n + 1) * TAM).map(i => `<url><loc>${new URL(urlIglesia(i), site).href}</loc></url>`);
  return new Response(`<?xml version="1.0" encoding="UTF-8"?>\n<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">\n${urls.join('\n')}\n</urlset>`, { headers: { 'content-type': 'application/xml' } });
};
