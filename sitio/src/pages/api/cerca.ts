// Iglesias cercanas a un punto. Busca en D1 por caja de coordenadas y ordena por distancia (haversine) en el Worker.
export const prerender = false;
import type { APIRoute } from 'astro';
import { urlIglesiaDe } from '../../lib/urls';
const json = (b: unknown, status = 200) => new Response(JSON.stringify(b), { status, headers: { 'content-type': 'application/json; charset=utf-8', 'cache-control': 'public, max-age=60, s-maxage=3600' } });
const RADIOS_M = [3000, 10000, 25000];
function dist(lat1: number, lon1: number, lat2: number, lon2: number) {
  const R = 6371000, r = Math.PI / 180, dLat = (lat2 - lat1) * r, dLon = (lon2 - lon1) * r;
  const a = Math.sin(dLat / 2) ** 2 + Math.cos(lat1 * r) * Math.cos(lat2 * r) * Math.sin(dLon / 2) ** 2;
  return 2 * R * Math.asin(Math.sqrt(a));
}
export const GET: APIRoute = async ({ url, locals }) => {
  const lat = parseFloat(url.searchParams.get('lat') ?? ''), lon = parseFloat(url.searchParams.get('lon') ?? '');
  if (!isFinite(lat) || !isFinite(lon) || Math.abs(lat) > 90 || Math.abs(lon) > 180) return json({ error: 'Coordenadas inválidas.' }, 400);
  const db = locals.runtime.env.DB;
  for (const radio of RADIOS_M) {
    const dLat = radio / 111320, dLon = radio / (111320 * Math.cos(lat * Math.PI / 180));
    const { results } = await db.prepare('SELECT datos, lat, lon FROM iglesias WHERE lat BETWEEN ?1 AND ?2 AND lon BETWEEN ?3 AND ?4 LIMIT 400')
      .bind(lat - dLat, lat + dLat, lon - dLon, lon + dLon).all<{ datos: string; lat: number; lon: number }>();
    const cercanas = results.map(r => ({ i: JSON.parse(r.datos), d: dist(lat, lon, r.lat, r.lon) })).filter(x => x.d <= radio).sort((a, b) => a.d - b.d).slice(0, 40);
    if (cercanas.length >= 5 || radio === RADIOS_M[RADIOS_M.length - 1]) {
      return json({ radio_m: radio, resultados: cercanas.map(({ i, d }) => ({ nombre: i.nombre, url: urlIglesiaDe(i.pais_slug, i.slug), distancia_m: Math.round(d), denominacion: i.denominacion, direccion: i.direccion, localidad: i.localidad, provincia: i.provincia, horarios: i.horarios, lat: i.lat, lon: i.lon })) });
    }
  }
  return json({ radio_m: RADIOS_M.at(-1), resultados: [] });
};
