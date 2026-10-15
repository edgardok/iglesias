import iglesiasJson from '../../../data/iglesias.json';

export type Iglesia = {
  slug: string; nombre: string; entidad: string; entidad_slug: string; filial: string | null;
  direccion: string; localidad: string; localidad_slug: string; provincia: string; provincia_slug: string;
  registro_ci: string | null; fuente: string;
  web: string | null; facebook: string | null; instagram: string | null; google_maps: string | null;
  telefono: string | null; email: string | null; horarios: string | null; lat: number | null; lon: number | null;
  reclamada: boolean; religion?: string | null; denominacion?: string | null; osm_id?: string | null;
};

export const iglesias = iglesiasJson as Iglesia[];

export type Grupo<T> = Map<string, T>;

const porProvincia = new Map<string, { nombre: string; slug: string; iglesias: Iglesia[] }>();
for (const i of iglesias) {
  const p = porProvincia.get(i.provincia_slug) ?? { nombre: i.provincia, slug: i.provincia_slug, iglesias: [] };
  p.iglesias.push(i); porProvincia.set(i.provincia_slug, p);
}
export const provincias = [...porProvincia.values()].sort((a, b) => a.nombre.localeCompare(b.nombre, 'es'));

export function localidadesDe(provSlug: string) {
  const m = new Map<string, { nombre: string; slug: string; iglesias: Iglesia[] }>();
  for (const i of porProvincia.get(provSlug)?.iglesias ?? []) {
    const l = m.get(i.localidad_slug) ?? { nombre: i.localidad, slug: i.localidad_slug, iglesias: [] };
    l.iglesias.push(i); m.set(i.localidad_slug, l);
  }
  return [...m.values()].sort((a, b) => b.iglesias.length - a.iglesias.length || a.nombre.localeCompare(b.nombre, 'es'));
}

export const urlIglesia = (i: Iglesia) => `/iglesia/${i.slug}/`;
export const urlProvincia = (s: string) => `/${s}/`;
export const urlLocalidad = (p: string, l: string) => `/${p}/${l}/`;
