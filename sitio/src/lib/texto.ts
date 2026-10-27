import type { Iglesia } from './datos';
import { urlIglesiaDe } from './urls';

/** Párrafo descriptivo en prosa, pensado para que un buscador o un LLM lo pueda citar tal cual. */
export function descripcion(i: Iglesia): string {
  const noCristiana = i.religion && i.religion !== 'Cristiana';
  const tipo = noCristiana ? `comunidad ${i.religion!.toLowerCase()}${i.denominacion && i.denominacion !== i.religion ? ` (${i.denominacion})` : ''}`
    : i.denominacion ? `iglesia de denominación ${i.denominacion}` : 'iglesia o comunidad de fe';
  const partes = [`${i.nombre} es una ${tipo} ubicada en ${i.localidad}, ${i.provincia}, ${i.pais}.`];
  if (i.direccion) partes.push(`Su dirección es ${i.direccion}, ${i.localidad}.`);
  if (i.filial) partes.push(`Es la filial ${i.filial} de ${i.entidad}, entidad inscripta en el registro de cultos de ${i.pais}${i.registro_ci ? ` con el número ${i.registro_ci}` : ''}.`);
  else if (i.registro_ci) partes.push(`Está inscripta en el registro de cultos de ${i.pais} con el número ${i.registro_ci}.`);
  if (i.horarios) partes.push(`Horarios de reunión: ${i.horarios}.`);
  if (i.telefono) partes.push(`Teléfono de contacto: ${i.telefono}.`);
  const redes = [i.web && 'sitio web', i.facebook && 'Facebook', i.instagram && 'Instagram'].filter(Boolean);
  if (redes.length) partes.push(`Tiene ${redes.join(', ')}.`);
  if (!i.horarios && !i.telefono) partes.push('Todavía no publicó horarios ni contacto en este directorio.');
  return partes.join(' ');
}

export function lineaMd(i: Iglesia, site: URL): string {
  const campos = [i.direccion && `Dirección: ${i.direccion}`, i.denominacion && `Denominación: ${i.denominacion}`, i.horarios && `Horarios: ${i.horarios}`,
    i.telefono && `Tel: ${i.telefono}`, i.web && `Web: ${i.web}`, i.facebook && `Facebook: ${i.facebook}`, i.instagram && `Instagram: ${i.instagram}`,
    i.lat && `Coordenadas: ${i.lat}, ${i.lon}`].filter(Boolean);
  return `- **${i.nombre}** (${new URL(urlIglesiaDe(i.pais_slug, i.slug), site).href})${campos.length ? '. ' + campos.join('. ') : ''}.`;
}

/** Ficha "delgada": sin localidad y sin ningún dato de contacto. Es una página casi vacía, así que no se indexa
 *  (noindex y fuera del sitemap). Sigue visible, enlazada desde las listas y presente en los datos abiertos.
 *  Una "dirección" que es solo el nombre de una calle, sin ciudad, no cuenta como dato. */
export function esDelgada(i: Iglesia): boolean {
  if (i.localidad_slug !== 'sin-localidad') return false;
  return !(i.telefono || i.web || i.email || i.horarios || i.facebook || i.instagram || i.google_maps);
}
