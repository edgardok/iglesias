// Worker con assets estáticos: sirve dist/ y enruta /api/* a los handlers (mismos que las Pages Functions).
import { onRequestPost as sumarse } from '../functions/api/sumarse';
import { onRequestGet as listar, onRequestPatch as marcar } from '../functions/api/solicitudes';

export default {
  async fetch(request: Request, env: any): Promise<Response> {
    const { pathname } = new URL(request.url);
    const ctx: any = { request, env, params: {}, data: {}, waitUntil() {}, passThroughOnException() {}, next: () => env.ASSETS.fetch(request), functionPath: pathname };
    if (pathname === '/api/sumarse' && request.method === 'POST') return sumarse(ctx);
    if (pathname === '/api/solicitudes' && request.method === 'GET') return listar(ctx);
    if (pathname === '/api/solicitudes' && request.method === 'PATCH') return marcar(ctx);
    if (pathname.startsWith('/api/')) return new Response('not found', { status: 404 });
    return env.ASSETS.fetch(request);
  },
};
