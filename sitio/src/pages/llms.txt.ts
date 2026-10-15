import { iglesias, paises, provinciasDe, localidadesDe, NOMBRE_SITIO } from '../lib/datos';
export const GET = ({ site }: { site: URL }) => {
  const u = (p: string) => new URL(p, site).href;
  const conHorarios = iglesias.filter(i => i.horarios).length, conGeo = iglesias.filter(i => i.lat).length;
  const locs = paises.flatMap(p => provinciasDe(p.slug).flatMap(r => localidadesDe(p.slug, r.slug).map(l => ({ p, r, l })))).sort((a, b) => b.l.iglesias.length - a.l.iglesias.length).slice(0, 60);
  return new Response(`# ${NOMBRE_SITIO}

> Directorio abierto y gratuito de ${iglesias.length.toLocaleString('es')} templos, iglesias y comunidades de fe de América Latina (evangélicas, católicas, judías, musulmanas, budistas y otras), con dirección, localidad, región, país, denominación y, cuando la iglesia los aportó, horarios, teléfono, web y redes. ${conGeo.toLocaleString('es')} fichas tienen coordenadas y ${conHorarios.toLocaleString('es')} tienen horarios. Países cubiertos hoy: ${paises.map(p => `${p.nombre} (${p.iglesias.length.toLocaleString('es')})`).join(', ')}. Fuentes: registros públicos de cada país, OpenStreetMap (ODbL) y datos enviados por las propias iglesias; cada país documenta sus fuentes en /<pais>/fuentes/. Los datos pueden estar desactualizados; cada ficha indica su fuente.

Cómo está organizado:
- Cada iglesia tiene una URL permanente en /<pais>/iglesia/<slug>/ con un párrafo descriptivo en prosa y JSON-LD schema.org PlaceOfWorship (dirección, geo, horarios, sameAs).
- Cada país tiene /<pais>/ (por región), /<pais>/tipo/<denominacion>/ y /<pais>/fuentes/.
- Cada localidad tiene una página HTML en /<pais>/<region>/<localidad>/ y una versión Markdown en /<pais>/<region>/<localidad>.md con todas sus iglesias y datos.
- Dataset en JSON, un archivo por región: /datos/<pais>/<region>.json (misma partición que el repositorio). Campos: pais, slug, nombre, entidad, denominacion, religion, direccion, localidad, provincia, lat, lon, horarios, telefono, email, web, facebook, instagram, google_maps, registro_ci. El dataset íntegro con fuentes crudas está en https://github.com/edgardok/iglesias/tree/main/data.
- Para sumar o corregir una iglesia: /sumarse/ (lo revisa un asistente y luego una persona).

## Países
${paises.map(p => `- [${p.nombre}](${u(`/${p.slug}/`)}): ${p.iglesias.length.toLocaleString('es')} fichas en ${provinciasDe(p.slug).length} ${p.region_nombre}s. Fuentes: ${u(`/${p.slug}/fuentes/`)}`).join('\n')}

## Localidades con más iglesias (Markdown)
${locs.map(({ p, r, l }) => `- [${l.nombre}, ${r.nombre}, ${p.nombre}](${u(`/${p.slug}/${r.slug}/${l.slug}.md`)}): ${l.iglesias.length}`).join('\n')}

## Sobre el proyecto
- [El movimiento: por qué existe este directorio y cómo sumarse](${u('/movimiento/')})

## Datos
- [Datos abiertos: JSON por país y por región](${u('/datos/')})
- [Fuentes y licencias](${u('/fuentes/')})
- [Sitemap](${u('/sitemap.xml')})
`, { headers: { 'content-type': 'text/plain; charset=utf-8' } });
};
