// Consultas a D1 para las páginas renderizadas en el Worker.
import type { Iglesia } from './datos';

type DB = { prepare(sql: string): { bind(...v: unknown[]): { first<T = any>(): Promise<T | null>; all<T = any>(): Promise<{ results: T[] }> } } };
const parse = (r: { datos: string }) => JSON.parse(r.datos) as Iglesia;

export async function iglesiaPorSlug(db: DB, pais: string, slug: string): Promise<Iglesia | null> {
  const r = await db.prepare('SELECT datos FROM iglesias WHERE pais_slug = ?1 AND slug = ?2').bind(pais, slug).first<{ datos: string }>();
  return r ? parse(r) : null;
}
export async function iglesiasDeLocalidad(db: DB, pais: string, prov: string, loc: string, limite = 150, desde = 0): Promise<{ total: number; lista: Iglesia[] }> {
  const t = await db.prepare('SELECT count(*) AS n FROM iglesias WHERE pais_slug = ?1 AND provincia_slug = ?2 AND localidad_slug = ?3').bind(pais, prov, loc).first<{ n: number }>();
  const { results } = await db.prepare('SELECT datos FROM iglesias WHERE pais_slug = ?1 AND provincia_slug = ?2 AND localidad_slug = ?3 ORDER BY nombre LIMIT ?4 OFFSET ?5').bind(pais, prov, loc, limite, desde).all<{ datos: string }>();
  return { total: t?.n ?? 0, lista: results.map(parse) };
}
export async function otrasEnLocalidad(db: DB, i: Iglesia, limite = 8): Promise<Iglesia[]> {
  const { results } = await db.prepare('SELECT datos FROM iglesias WHERE pais_slug = ?1 AND provincia_slug = ?2 AND localidad_slug = ?3 AND slug != ?4 ORDER BY nombre LIMIT ?5').bind(i.pais_slug, i.provincia_slug, i.localidad_slug, i.slug, limite).all<{ datos: string }>();
  return results.map(parse);
}
export const db = (locals: any): DB => locals.runtime.env.DB;
export const CACHE = 'public, max-age=300, s-maxage=86400, stale-while-revalidate=604800';
