import { iglesias, provincias } from '../lib/datos';
export const GET = () => new Response(`# Iglesias de Argentina

> Directorio abierto de ${iglesias.length} templos, iglesias y comunidades de fe de Argentina, con dirección, localidad, provincia y, cuando la iglesia los aportó, horarios, contacto y redes. Fuentes: Registro Nacional de Cultos (Cancillería Argentina) y OpenStreetMap, más datos enviados por las propias iglesias.

Cada ficha está en /iglesia/<slug>/ e incluye JSON-LD schema.org PlaceOfWorship.
Dataset completo en JSON: /datos/iglesias.json

## Provincias
${provincias.map(p => `- [${p.nombre}](/${p.slug}/): ${p.iglesias.length} fichas`).join('\n')}

## Para sumar o corregir una iglesia
- [Formulario](/sumarse/)
`, { headers: { 'content-type': 'text/plain; charset=utf-8' } });
