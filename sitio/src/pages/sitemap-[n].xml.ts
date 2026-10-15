import { iglesias, urlIglesia } from '../lib/datos';
export const TAM = 10000;
export function getStaticPaths() { return Array.from({ length: Math.ceil(iglesias.length / TAM) }, (_, n) => ({ params: { n: String(n) } })); }
export const GET = ({ params, site }: { params: { n: string }; site: URL }) => {
  const n = Number(params.n);
  const urls = iglesias.slice(n * TAM, (n + 1) * TAM).map(i => `<url><loc>${new URL(urlIglesia(i), site).href}</loc></url>`);
  return new Response(`<?xml version="1.0" encoding="UTF-8"?>\n<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">\n${urls.join('\n')}\n</urlset>`, { headers: { 'content-type': 'application/xml' } });
};
