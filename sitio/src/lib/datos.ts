// Carga todos los países: data/<iso>/iglesias.json + data/<iso>/fuentes.json
const archivos = import.meta.glob('../../../data/*/iglesias/*.json', { eager: true, import: 'default' }) as Record<string, Iglesia[]>;
const archivosFuentes = import.meta.glob('../../../data/*/fuentes.json', { eager: true, import: 'default' }) as Record<string, Fuentes>;

export type Iglesia = {
  slug: string; nombre: string; entidad: string; entidad_slug: string; filial: string | null;
  direccion: string; localidad: string; localidad_slug: string; provincia: string; provincia_slug: string;
  pais: string; pais_slug: string;
  registro_ci: string | null; fuente: string;
  web: string | null; facebook: string | null; instagram: string | null; google_maps: string | null;
  telefono: string | null; email: string | null; horarios: string | null; lat: number | null; lon: number | null;
  reclamada: boolean; religion?: string | null; denominacion?: string | null; osm_id?: string | null; geo_fuente?: string | null;
};
export type Fuente = { nombre: string; organismo?: string; url?: string; archivo?: string; descarga?: string; licencia?: string; que_aporta?: string; script?: string; limitaciones?: string };
export type Fuentes = { pais: string; iso: string; region_nombre: string; actualizado: string; fuentes: Fuente[]; pendientes?: string[] };
export type Pais = { nombre: string; slug: string; region_nombre: string; iglesias: Iglesia[]; fuentes: Fuentes | null };

export const iglesias: Iglesia[] = Object.values(archivos).flat();

const fuentesPorIso = new Map<string, Fuentes>();
for (const [ruta, f] of Object.entries(archivosFuentes)) fuentesPorIso.set(ruta.split('/').at(-2)!, f);

const porPais = new Map<string, Pais>();
for (const i of iglesias) {
  const p = porPais.get(i.pais_slug) ?? { nombre: i.pais, slug: i.pais_slug, region_nombre: fuentesPorIso.get(i.pais_slug)?.region_nombre ?? 'región', iglesias: [], fuentes: fuentesPorIso.get(i.pais_slug) ?? null };
  p.iglesias.push(i); porPais.set(i.pais_slug, p);
}
export const paises = [...porPais.values()].sort((a, b) => a.nombre.localeCompare(b.nombre, 'es'));

/** Países de América Latina y su estado de cobertura, para la portada. */
export const PAISES_LATAM: { nombre: string; slug: string }[] = [
  { nombre: 'Argentina', slug: 'ar' }, { nombre: 'Bolivia', slug: 'bo' }, { nombre: 'Brasil', slug: 'br' }, { nombre: 'Chile', slug: 'cl' }, { nombre: 'Colombia', slug: 'co' },
  { nombre: 'Costa Rica', slug: 'cr' }, { nombre: 'Cuba', slug: 'cu' }, { nombre: 'Ecuador', slug: 'ec' }, { nombre: 'El Salvador', slug: 'sv' }, { nombre: 'Guatemala', slug: 'gt' },
  { nombre: 'Honduras', slug: 'hn' }, { nombre: 'México', slug: 'mx' }, { nombre: 'Nicaragua', slug: 'ni' }, { nombre: 'Panamá', slug: 'pa' }, { nombre: 'Paraguay', slug: 'py' },
  { nombre: 'Perú', slug: 'pe' }, { nombre: 'Puerto Rico', slug: 'pr' }, { nombre: 'República Dominicana', slug: 'do' }, { nombre: 'Uruguay', slug: 'uy' }, { nombre: 'Venezuela', slug: 've' },
];

export function provinciasDe(paisSlug: string) {
  const m = new Map<string, { nombre: string; slug: string; iglesias: Iglesia[] }>();
  for (const i of porPais.get(paisSlug)?.iglesias ?? []) {
    const p = m.get(i.provincia_slug) ?? { nombre: i.provincia, slug: i.provincia_slug, iglesias: [] };
    p.iglesias.push(i); m.set(i.provincia_slug, p);
  }
  return [...m.values()].sort((a, b) => a.nombre.localeCompare(b.nombre, 'es'));
}

export function localidadesDe(paisSlug: string, provSlug: string) {
  const m = new Map<string, { nombre: string; slug: string; iglesias: Iglesia[] }>();
  for (const i of porPais.get(paisSlug)?.iglesias ?? []) {
    if (i.provincia_slug !== provSlug) continue;
    const l = m.get(i.localidad_slug) ?? { nombre: i.localidad, slug: i.localidad_slug, iglesias: [] };
    l.iglesias.push(i); m.set(i.localidad_slug, l);
  }
  return [...m.values()].sort((a, b) => b.iglesias.length - a.iglesias.length || a.nombre.localeCompare(b.nombre, 'es'));
}

export function tiposDe(lista: Iglesia[]) {
  const m = new Map<string, { nombre: string; slug: string; iglesias: Iglesia[] }>();
  for (const i of lista) { const d = i.denominacion ?? 'Sin clasificar'; const k = slugify(d); const g = m.get(k) ?? { nombre: d, slug: k, iglesias: [] }; g.iglesias.push(i); m.set(k, g); }
  return [...m.values()].sort((a, b) => b.iglesias.length - a.iglesias.length);
}

export const urlPais = (p: string) => `/${p}/`;
export const urlProvincia = (p: string, s: string) => `/${p}/${s}/`;
export const urlLocalidad = (p: string, s: string, l: string) => `/${p}/${s}/${l}/`;
export const urlIglesia = (i: Iglesia) => `/${i.pais_slug}/iglesia/${i.slug}/`;
export const urlTipo = (p: string, t: string) => `/${p}/tipo/${t}/`;

export function slugify(s: string) {
  return s.normalize('NFKD').replace(/[̀-ͯ]/g, '').replace(/[^a-zA-Z0-9]+/g, '-').replace(/^-|-$/g, '').toLowerCase();
}

export const NOMBRE_SITIO = 'Iglesias de América Latina';
