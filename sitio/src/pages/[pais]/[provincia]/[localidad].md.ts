export const prerender = false;
import type { APIRoute } from 'astro';
import { db, iglesiasDeLocalidad, CACHE } from '../../../lib/d1';
import { lineaMd } from '../../../lib/texto';
import { fuentesPorPais } from '../../../lib/fuentes';
const POR_PAGINA = 500;
export const GET: APIRoute = async ({ params, locals, site, url }) => {
  const pag = Math.min(Math.max(parseInt(url.searchParams.get('p') ?? '1') || 1, 1), 5000);
  const { total, lista } = await iglesiasDeLocalidad(db(locals), params.pais!, params.provincia!, params.localidad!, POR_PAGINA, (pag - 1) * POR_PAGINA);
  if (!lista.length) return new Response('Localidad no encontrada', { status: 404 });
  const paginas = Math.ceil(total / POR_PAGINA);
  const i0 = lista[0];
  const fuentes = (fuentesPorPais.get(params.pais!)?.fuentes ?? []).map(f => f.nombre).join(', ');
  const md = `# Iglesias en ${i0.localidad}, ${i0.provincia}, ${i0.pais}\n\n${total.toLocaleString('es')} iglesias, templos y comunidades de fe registradas en este directorio abierto${paginas > 1 ? ` (página ${pag} de ${paginas})` : ''}. Fuentes: ${fuentes}. Licencia ODbL. Página web: ${new URL(`/${params.pais}/${params.provincia}/${params.localidad}/`, site).href}\n\n${lista.map(i => lineaMd(i, site!)).join('\n')}\n${pag < paginas ? `\nSiguiente página: ${new URL(`/${params.pais}/${params.provincia}/${params.localidad}.md?p=${pag + 1}`, site).href}\n` : ''}`;
  return new Response(md, { headers: { 'content-type': 'text/markdown; charset=utf-8', 'cache-control': CACHE } });
};
