export const prerender = false;
import type { APIRoute } from 'astro';
import { db, iglesiasDeLocalidad, CACHE } from '../../../lib/d1';
import { lineaMd } from '../../../lib/texto';
import { fuentesPorPais } from '../../../lib/fuentes';
export const GET: APIRoute = async ({ params, locals, site }) => {
  const lista = await iglesiasDeLocalidad(db(locals), params.pais!, params.provincia!, params.localidad!);
  if (!lista.length) return new Response('Localidad no encontrada', { status: 404 });
  const i0 = lista[0];
  const fuentes = (fuentesPorPais.get(params.pais!)?.fuentes ?? []).map(f => f.nombre).join(', ');
  const md = `# Iglesias en ${i0.localidad}, ${i0.provincia}, ${i0.pais}\n\n${lista.length} iglesias, templos y comunidades de fe registradas en este directorio abierto. Fuentes: ${fuentes}. Licencia ODbL. Página web: ${new URL(`/${params.pais}/${params.provincia}/${params.localidad}/`, site).href}\n\n${lista.map(i => lineaMd(i, site!)).join('\n')}\n`;
  return new Response(md, { headers: { 'content-type': 'text/markdown; charset=utf-8', 'cache-control': CACHE } });
};
