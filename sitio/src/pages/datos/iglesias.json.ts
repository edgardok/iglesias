import { iglesias } from '../../lib/datos';
export const GET = () => new Response(JSON.stringify(iglesias), { headers: { 'content-type': 'application/json; charset=utf-8', 'access-control-allow-origin': '*' } });
