import { provincias, localidadesDe } from '../../lib/datos';
import { lineaMd } from '../../lib/texto';
export function getStaticPaths() {
  return provincias.flatMap(p => localidadesDe(p.slug).map(l => ({ params: { provincia: p.slug, localidad: l.slug }, props: { p, l } })));
}
export const GET = ({ props, site }: { props: any; site: URL }) => {
  const { p, l } = props;
  const lista = [...l.iglesias].sort((a: any, b: any) => a.nombre.localeCompare(b.nombre, 'es'));
  const md = `# Iglesias en ${l.nombre}, ${p.nombre} (Argentina)\n\n${lista.length} iglesias, templos y comunidades de fe registradas en este directorio abierto. Fuente: Registro Nacional de Cultos, OpenStreetMap y aportes de las iglesias. Licencia ODbL. Página web: ${new URL(`/${p.slug}/${l.slug}/`, site).href}\n\n${lista.map((i: any) => lineaMd(i, site)).join('\n')}\n`;
  return new Response(md, { headers: { 'content-type': 'text/markdown; charset=utf-8' } });
};
