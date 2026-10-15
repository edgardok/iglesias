// Dataset completo por región (provincia / departamento / estado).
import { paises, provinciasDe } from '../../../lib/datos';
export function getStaticPaths() { return paises.flatMap(p => provinciasDe(p.slug).map(r => ({ params: { pais: p.slug, provincia: r.slug }, props: { r } }))); }
export const GET = ({ props }: { props: any }) => new Response(JSON.stringify(props.r.iglesias), { headers: { 'content-type': 'application/json; charset=utf-8', 'access-control-allow-origin': '*' } });
