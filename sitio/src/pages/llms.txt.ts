import { iglesias, paises, provinciasDe, localidadesDe, listaPaises, esLatam, NOMBRE_SITIO } from '../lib/datos';
export const GET = ({ site }: { site: URL }) => {
  const u = (p: string) => new URL(p, site).href;
  const hisp = iglesias.filter(i => esLatam(i.pais_slug));
  const conHorarios = hisp.filter(i => i.horarios).length, conGeo = hisp.filter(i => i.lat).length;
  const locs = paises.flatMap(p => provinciasDe(p.slug).flatMap(r => localidadesDe(p.slug, r.slug).map(l => ({ p, r, l })))).sort((a, b) => b.l.iglesias.length - a.l.iglesias.length).slice(0, 60);
  return new Response(`# ${NOMBRE_SITIO}

> Directorio abierto y gratuito de ${hisp.length.toLocaleString('es')} iglesias evangélicas y otras comunidades de fe de América Latina (bautistas, pentecostales, adventistas, judías, musulmanas y otras; no incluye parroquias católicas), con dirección, localidad, región, país, denominación y, cuando la iglesia los aportó, horarios, teléfono, web y redes. ${conGeo.toLocaleString('es')} fichas tienen coordenadas y ${conHorarios.toLocaleString('es')} tienen horarios. Países cubiertos hoy: ${listaPaises(paises.filter(p => esLatam(p.slug)).map(p => `${p.nombre} (${p.iglesias.length.toLocaleString('es')})`))}. Fuentes: registros públicos de cada país, OpenStreetMap (ODbL) y datos enviados por las propias iglesias; cada país documenta sus fuentes en /<pais>/fuentes/. Los datos pueden estar desactualizados; cada ficha indica su fuente.

Cómo está organizado:
- La portada (/) presenta el proyecto; el índice navegable está en /directorio/ y la búsqueda por cercanía en /cerca/ (API: /api/cerca?lat=&lon=).
- Cada iglesia tiene una URL permanente en /<pais>/iglesia/<slug>/ con un párrafo descriptivo en prosa y JSON-LD schema.org PlaceOfWorship (dirección, geo, horarios, sameAs).
- Cada país tiene /<pais>/ (por región), /<pais>/tipo/<denominacion>/ y /<pais>/fuentes/.
- Cada localidad tiene una página HTML en /<pais>/<region>/<localidad>/ y una versión Markdown en /<pais>/<region>/<localidad>.md con sus iglesias y datos. Las listas largas se paginan con ?p=2, ?p=3. Las iglesias cuya localidad no pudo determinarse están en /<pais>/<region>/sin-localidad/.
- Dataset en JSON, un archivo por región: /datos/<pais>/<region>.json, sin campos vacíos y en partes (-2, -3) si la región es muy grande. Índice en /datos/. Campos: pais, slug, nombre, entidad, denominacion, religion, direccion, localidad, provincia, lat, lon, horarios, telefono, email, web, facebook, instagram, google_maps, registro_ci. El dataset íntegro con fuentes crudas está en https://github.com/edgardok/iglesias/tree/main/data.
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
