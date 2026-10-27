import { TAM, indexables } from './sitemap-[n].xml';
export const GET = ({ site }: { site: URL }) => {
  const partes = Math.ceil(indexables.length / TAM);
  const index = `<?xml version="1.0" encoding="UTF-8"?>\n<sitemapindex xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">\n<sitemap><loc>${new URL('/sitemap-paginas.xml', site).href}</loc></sitemap>\n${Array.from({ length: partes }, (_, n) => `<sitemap><loc>${new URL(`/sitemap-${n}.xml`, site).href}</loc></sitemap>`).join('\n')}\n</sitemapindex>`;
  return new Response(index, { headers: { 'content-type': 'application/xml' } });
};
