import { paises, provinciasDe, localidadesDe, tiposDe } from '../lib/datos';
export const GET = ({ site }: { site: URL }) => {
  const u = (p: string) => `<url><loc>${new URL(p, site).href}</loc></url>`;
  const urls = ['/', '/movimiento/', '/apoyar/', '/paises/', '/sumarse/', '/datos/', '/fuentes/',
    ...paises.flatMap(p => [`/${p.slug}/`, `/${p.slug}/fuentes/`, `/${p.slug}/tipo/`, ...tiposDe(p.iglesias).map(t => `/${p.slug}/tipo/${t.slug}/`),
      ...provinciasDe(p.slug).flatMap(r => [`/${p.slug}/${r.slug}/`, ...localidadesDe(p.slug, r.slug).flatMap(l => [`/${p.slug}/${r.slug}/${l.slug}/`, `/${p.slug}/${r.slug}/${l.slug}.md`])])])];
  return new Response(`<?xml version="1.0" encoding="UTF-8"?>\n<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">\n${urls.map(u).join('\n')}\n</urlset>`, { headers: { 'content-type': 'application/xml' } });
};
