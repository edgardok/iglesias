import { provincias, localidadesDe } from '../lib/datos';
export const GET = ({ site }: { site: URL }) => {
  const u = (p: string) => `<url><loc>${new URL(p, site).href}</loc></url>`;
  const urls = ['/', '/provincias/', '/sumarse/', '/datos/', '/tipo/', ...provincias.flatMap(p => [`/${p.slug}/`, ...localidadesDe(p.slug).flatMap(l => [`/${p.slug}/${l.slug}/`, `/${p.slug}/${l.slug}.md`])])];
  return new Response(`<?xml version="1.0" encoding="UTF-8"?>\n<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">\n${urls.map(u).join('\n')}\n</urlset>`, { headers: { 'content-type': 'application/xml' } });
};
