// Cloudflare Pages Function: recibe el formulario, valida Turnstile y guarda en D1.
interface Env { DB: D1Database; TURNSTILE_SECRET_KEY: string }

const CAMPOS = ['pais','slug','nombre','denominacion','direccion','localidad','provincia','horarios','telefono','email','facebook','instagram','google_maps','web','contacto_nombre','contacto_email','comentario'] as const;
const json = (b: unknown, status = 200) => new Response(JSON.stringify(b), { status, headers: { 'content-type': 'application/json; charset=utf-8' } });

export const onRequestPost: PagesFunction<Env> = async ({ request, env }) => {
  const form = await request.formData();
  const token = String(form.get('cf-turnstile-response') ?? '');
  const ip = request.headers.get('CF-Connecting-IP') ?? '';
  if (!token) return json({ error: 'Completá la verificación anti-bots.' }, 400);

  const ver = await fetch('https://challenges.cloudflare.com/turnstile/v0/siteverify', {
    method: 'POST', headers: { 'content-type': 'application/json' },
    body: JSON.stringify({ secret: env.TURNSTILE_SECRET_KEY ?? '1x0000000000000000000000000000000AA', response: token, remoteip: ip }),
  }).then(r => r.json() as Promise<{ success: boolean }>);
  if (!ver.success) return json({ error: 'La verificación anti-bots falló. Recargá la página e intentá de nuevo.' }, 403);

  const datos: Record<string, string> = {};
  for (const c of CAMPOS) datos[c] = String(form.get(c) ?? '').trim().slice(0, 1000);
  if (!datos.pais || !datos.nombre || !datos.localidad || !datos.provincia || !datos.contacto_email) return json({ error: 'Faltan campos obligatorios.' }, 400);
  for (const u of ['facebook','instagram','google_maps','web']) if (datos[u] && !/^https?:\/\//i.test(datos[u])) return json({ error: `El enlace de ${u} no es válido.` }, 400);

  const id = crypto.randomUUID();
  await env.DB.prepare('INSERT INTO solicitudes (id, creado, estado, ip_hash, datos) VALUES (?1, ?2, ?3, ?4, ?5)')
    .bind(id, new Date().toISOString(), 'pendiente', await sha256(ip), JSON.stringify(datos)).run();
  return json({ ok: true, id });
};

async function sha256(s: string) {
  const h = await crypto.subtle.digest('SHA-256', new TextEncoder().encode(s));
  return [...new Uint8Array(h)].map(b => b.toString(16).padStart(2, '0')).join('');
}
