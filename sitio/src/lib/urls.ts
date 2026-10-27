// Helpers sin datos: se pueden importar desde páginas renderizadas en el Worker sin arrastrar el dataset.
export const NOMBRE_SITIO = 'Iglesias en español';
export const urlPais = (p: string) => `/${p}/`;
export const urlProvincia = (p: string, s: string) => `/${p}/${s}/`;
export const urlLocalidad = (p: string, s: string, l: string) => `/${p}/${s}/${l}/`;
export const urlIglesiaDe = (pais_slug: string, slug: string) => `/${pais_slug}/iglesia/${slug}/`;
export const urlTipo = (p: string, t: string) => `/${p}/tipo/${t}/`;
export function slugify(s: string) {
  return s.normalize('NFKD').replace(/[̀-ͯ]/g, '').replace(/[^a-zA-Z0-9]+/g, '-').replace(/^-|-$/g, '').toLowerCase();
}
