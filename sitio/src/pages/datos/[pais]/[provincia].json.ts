// Dataset por región, sin campos vacíos y en trozos de CHUNK_DATOS fichas (Cloudflare limita cada archivo a 25 MiB).
import { paises, provinciasDe, CHUNK_DATOS, clavesDatos } from '../../../lib/datos';
export function getStaticPaths() {
  return paises.flatMap(p => provinciasDe(p.slug).flatMap(r =>
    Array.from({ length: Math.ceil(r.iglesias.length / CHUNK_DATOS) }, (_, k) => ({
      params: { pais: p.slug, provincia: clavesDatos(r.slug, k) }, props: { lista: r.iglesias.slice(k * CHUNK_DATOS, (k + 1) * CHUNK_DATOS) } }))));
}
export const GET = ({ props }: { props: any }) => {
  const compacto = props.lista.map((i: any) => Object.fromEntries(Object.entries(i).filter(([, v]) => v !== null && v !== false && v !== '')));
  return new Response(JSON.stringify(compacto), { headers: { 'content-type': 'application/json; charset=utf-8', 'access-control-allow-origin': '*' } });
};
