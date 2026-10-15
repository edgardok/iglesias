import { paises } from '../../lib/datos';
export function getStaticPaths() { return paises.map(p => ({ params: { pais: p.slug }, props: { p } })); }
export const GET = ({ props }: { props: any }) => new Response(JSON.stringify(props.p.iglesias), { headers: { 'content-type': 'application/json; charset=utf-8', 'access-control-allow-origin': '*' } });
