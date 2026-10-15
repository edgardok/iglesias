// Endpoint para el agente: lista solicitudes pendientes y permite marcar estado. Protegido con token.
interface Env { DB: D1Database; AGENTE_TOKEN: string }
const json = (b: unknown, status = 200) => new Response(JSON.stringify(b), { status, headers: { 'content-type': 'application/json; charset=utf-8' } });
const autorizado = (r: Request, env: Env) => env.AGENTE_TOKEN && r.headers.get('authorization') === `Bearer ${env.AGENTE_TOKEN}`;

export const onRequestGet: PagesFunction<Env> = async ({ request, env }) => {
  if (!autorizado(request, env)) return json({ error: 'no autorizado' }, 401);
  const estado = new URL(request.url).searchParams.get('estado') ?? 'pendiente';
  const { results } = await env.DB.prepare('SELECT id, creado, estado, datos FROM solicitudes WHERE estado = ?1 ORDER BY creado LIMIT 100').bind(estado).all();
  return json(results.map((r: any) => ({ ...r, datos: JSON.parse(r.datos) })));
};

export const onRequestPatch: PagesFunction<Env> = async ({ request, env }) => {
  if (!autorizado(request, env)) return json({ error: 'no autorizado' }, 401);
  const { id, estado, resolucion } = await request.json() as { id: string; estado: string; resolucion?: unknown };
  if (!['aprobada','rechazada','revisar'].includes(estado)) return json({ error: 'estado inválido' }, 400);
  await env.DB.prepare('UPDATE solicitudes SET estado = ?2, resolucion = ?3, resuelto = ?4 WHERE id = ?1')
    .bind(id, estado, JSON.stringify(resolucion ?? null), new Date().toISOString()).run();
  return json({ ok: true });
};
