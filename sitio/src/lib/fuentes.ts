import type { Fuentes } from './datos';
const archivos = import.meta.glob('../../../data/*/fuentes.json', { eager: true, import: 'default' }) as Record<string, Fuentes>;
export const fuentesPorPais = new Map<string, Fuentes>();
for (const [ruta, f] of Object.entries(archivos)) fuentesPorPais.set(ruta.split('/').at(-2)!, f);
