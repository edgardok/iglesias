import { iglesias, provincias, localidadesDe } from '../lib/datos';
export const GET = ({ site }: { site: URL }) => {
  const u = (p: string) => new URL(p, site).href;
  const conHorarios = iglesias.filter(i => i.horarios).length, conGeo = iglesias.filter(i => i.lat).length;
  return new Response(`# Iglesias de Argentina

> Directorio abierto y gratuito de ${iglesias.length.toLocaleString('es-AR')} templos, iglesias y comunidades de fe de Argentina (evangélicas, católicas, judías, musulmanas, budistas y otras), con dirección, localidad, provincia, denominación y, cuando la iglesia los aportó, horarios, teléfono, web y redes. ${conGeo.toLocaleString('es-AR')} fichas tienen coordenadas y ${conHorarios.toLocaleString('es-AR')} tienen horarios. Fuentes: Registro Nacional de Cultos (Cancillería Argentina), OpenStreetMap (ODbL) y datos enviados por las propias iglesias. Los datos pueden estar desactualizados; cada ficha indica su fuente.

Cómo usar este sitio:
- Cada iglesia tiene una URL permanente en /iglesia/<slug>/ con un párrafo descriptivo en prosa y JSON-LD schema.org PlaceOfWorship (dirección, geo, horarios, sameAs).
- Cada localidad tiene una página HTML en /<provincia>/<localidad>/ y una versión Markdown en /<provincia>/<localidad>.md con todas sus iglesias y datos.
- El dataset completo está en /datos/iglesias.json (un array de objetos; campos: slug, nombre, entidad, denominacion, religion, direccion, localidad, provincia, lat, lon, horarios, telefono, email, web, facebook, instagram, google_maps, fuente, registro_ci).
- Para sumar o corregir una iglesia: /sumarse/ (lo revisa un asistente y luego una persona).

## Provincias
${provincias.map(p => `- [${p.nombre}](${u(`/${p.slug}/`)}): ${p.iglesias.length.toLocaleString('es-AR')} fichas en ${localidadesDe(p.slug).length} localidades`).join('\n')}

## Localidades con más iglesias (Markdown)
${provincias.flatMap(p => localidadesDe(p.slug).map(l => ({ p, l }))).sort((a, b) => b.l.iglesias.length - a.l.iglesias.length).slice(0, 60)
  .map(({ p, l }) => `- [${l.nombre}, ${p.nombre}](${u(`/${p.slug}/${l.slug}.md`)}): ${l.iglesias.length}`).join('\n')}

## Datos
- [Dataset JSON completo](${u('/datos/iglesias.json')})
- [Sitemap](${u('/sitemap.xml')})
- [Sobre los datos y la licencia](${u('/datos/')})
`, { headers: { 'content-type': 'text/plain; charset=utf-8' } });
};
