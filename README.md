# Iglesias de Argentina: directorio abierto

MVP de un directorio estático con una ficha por templo, pensado para que buscadores y asistentes de IA
puedan leer qué iglesias hay en cada localidad. Datos del Registro Nacional de Cultos y OpenStreetMap,
completados por las propias iglesias a través de un formulario.

## Estructura

- `data/raw/`: fuentes tal como se bajaron (CSV de Cancillería, JSON de Overpass). No se editan.
- `data/iglesias.json`: el dataset normalizado. Es la única fuente de verdad del sitio.
- `scripts/normalizar.py`: CSV oficial a JSON.
- `scripts/enriquecer_osm.py`: fusiona OpenStreetMap y asigna provincia y municipio con la API georef.
- `sitio/`: Astro (estático) + Worker de Cloudflare para el formulario.
  - `src/pages/`: inicio, provincias, localidades, ficha por iglesia, formulario, robots, llms.txt, sitemap, datos.
  - `functions/api/`: handlers del formulario (Turnstile + D1) y del endpoint para el agente.
  - `worker/index.ts`: enruta `/api/*` a los handlers y sirve el resto como assets.
  - `agente/procesar.ts`: agente con Claude que revisa las solicitudes y actualiza `data/iglesias.json`.

## Regenerar datos

```bash
python3 -I scripts/normalizar.py data/raw/registro-culto-export.csv data/iglesias.json
python3 -I scripts/enriquecer_osm.py data/raw/osm-place-of-worship.json data/iglesias.json
```

## Sitio

```bash
cd sitio && npm install && npm run build && npm run dev
```

## Desplegar en Cloudflare (gratis)

1. `npx wrangler login`
2. `npx wrangler d1 create iglesias-ar` y pegar el `database_id` en `wrangler.toml`.
3. `npx wrangler d1 execute iglesias-ar --file=schema.sql --remote`
4. Crear un sitio en Turnstile (dashboard de Cloudflare), y:
   `npx wrangler secret put TURNSTILE_SECRET_KEY`, `npx wrangler secret put AGENTE_TOKEN`,
   exportar `PUBLIC_TURNSTILE_SITE_KEY` antes del build.
5. `npm run deploy`

Se usa Workers con assets estáticos y no Pages porque el sitio tiene unas 42.000 páginas y Pages corta en 20.000 archivos.

## Agente

```bash
cd sitio
npx tsx agente/procesar.ts --local agente/ejemplo-solicitudes.json --dry-run   # prueba sin tocar nada
API_BASE=https://<worker>.workers.dev AGENTE_TOKEN=... npx tsx agente/procesar.ts
```

Necesita credenciales de la API de Anthropic (`ANTHROPIC_API_KEY` o `ant auth login`). El agente escribe en
`data/iglesias.json` y marca las solicitudes; publicar sigue siendo un commit y un deploy hechos por una persona.

## Pendiente

- Correr el agente contra solicitudes reales (no se probó por falta de API key en esta máquina).
- Parroquias católicas: solo las que están en OpenStreetMap. Falta la guía de AICA o las diócesis.
- Geocodificar las fichas del registro oficial (hoy solo tienen coordenadas las de OSM).
- Dominio propio y envío de email a quien reclama la ficha cuando se publica.
