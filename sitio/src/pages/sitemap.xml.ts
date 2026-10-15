import { provincias, localidadesDe } from '../lib/datos';
import { TAM } from './sitemap-[n].xml';
import { iglesias } from '../lib/datos';
export const GET = ({ site }: { site: URL }) => {
  const u = (p: string) => `<url><loc>${new URL(p, site).href}</loc></url>`;
  const estaticas = ['/', '/provincias/', '/sumarse/', '/datos/', '/llms.txt',
    ...provincias.flatMap(p => [`/${p.slug}/`, ...localidadesDe(p.slug).flatMap(l => [`/${p.slug}/${l.slug}/`, `/${p.slug}/${l.slug}.md`])])];
  const partes = Math.ceil(iglesias.length / TAM);
  const index = `<?xml version="1.0" encoding="UTF-8"?>\n<sitemapindex xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">\n<sitemap><loc>${new URL('/sitemap-paginas.xml', site).href}</loc></sitemap>\n${Array.from({ length: partes }, (_, n) => `<sitemap><loc>${new URL(`/sitemap-${n}.xml`, site).href}</loc></sitemap>`).join('\n')}\n</sitemapindex>`;
  return new Response(index, { headers: { 'content-type': 'application/xml' } });
};
