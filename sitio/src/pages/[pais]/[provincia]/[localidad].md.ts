import { paises, provinciasDe, localidadesDe } from '../../../lib/datos';
import { lineaMd } from '../../../lib/texto';
export function getStaticPaths() {
  return paises.flatMap(p => provinciasDe(p.slug).flatMap(r => localidadesDe(p.slug, r.slug).map(l => ({ params: { pais: p.slug, provincia: r.slug, localidad: l.slug }, props: { p, r, l } }))));
}
export const GET = ({ props, site }: { props: any; site: URL }) => {
  const { p, r, l } = props;
  const lista = [...l.iglesias].sort((a: any, b: any) => a.nombre.localeCompare(b.nombre, 'es'));
  const md = `# Iglesias en ${l.nombre}, ${r.nombre}, ${p.nombre}\n\n${lista.length} iglesias, templos y comunidades de fe registradas en este directorio abierto. Fuentes: ${(p.fuentes?.fuentes ?? []).map((f: any) => f.nombre).join(', ')}. Licencia ODbL. Página web: ${new URL(`/${p.slug}/${r.slug}/${l.slug}/`, site).href}\n\n${lista.map((i: any) => lineaMd(i, site)).join('\n')}\n`;
  return new Response(md, { headers: { 'content-type': 'text/markdown; charset=utf-8' } });
};
