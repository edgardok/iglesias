// Índice liviano de localidades para el autocompletado del buscador de la portada.
import { paises, provinciasDe, localidadesDe } from '../../lib/datos';
export const GET = () => {
  const out = paises.flatMap(p => provinciasDe(p.slug).flatMap(r => localidadesDe(p.slug, r.slug)
    .filter(l => l.slug !== 'sin-localidad')
    .map(l => ({ p: p.slug, pn: p.nombre, r: r.slug, rn: r.nombre, l: l.slug, ln: l.nombre, n: l.iglesias.length }))));
  return new Response(JSON.stringify(out), { headers: { 'content-type': 'application/json; charset=utf-8', 'cache-control': 'public, max-age=86400' } });
};
