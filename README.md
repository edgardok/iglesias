# Iglesias de Argentina: directorio abierto

MVP de un directorio estático con una ficha por templo, pensado para que buscadores y asistentes de IA
puedan leer qué iglesias hay en cada localidad. Datos del Registro Nacional de Cultos y OpenStreetMap,
completados por las propias iglesias a través de un formulario.

## Estructura

- `data/raw/`: fuentes tal como se bajaron (CSV de Cancillería, JSON de Overpass). No se editan.
- `data/iglesias.json`: el dataset normalizado. Es la única fuente de verdad del sitio.
- `scripts/normalizar.py`: CSV oficial a JSON.
- `scripts/enriquecer_osm.py`: fusiona OpenStreetMap y asigna provincia y municipio con la API georef.
- `scripts/denominacion.py`: normaliza la denominación de OSM e infiere la del resto a partir del nombre.
- `scripts/geocodificar.py` + `scripts/aplicar_geo.py`: geocodifican direcciones del registro con georef (solo con filtro de localidad o departamento; sin filtro georef ubica mal). Resultado en `data/geo.json`.
- `sitio/`: Astro (estático) + Worker de Cloudflare para el formulario.
  - `src/pages/`: inicio, provincias, localidades (HTML y `.md`), tipo/denominación, ficha por iglesia, formulario, robots, llms.txt, sitemap index, datos.
  - `functions/api/`: handlers del formulario (Turnstile + D1) y del endpoint para el agente.
  - `worker/index.ts`: enruta `/api/*` a los handlers y sirve el resto como assets.
  - `agente/procesar.ts`: agente con Claude que revisa las solicitudes y actualiza `data/iglesias.json`.

## Optimización para buscadores y LLMs

- Una URL permanente por iglesia: `/iglesia/<slug>/`, con un párrafo en prosa que resume todo lo que se sabe de ella y JSON-LD (`PlaceOfWorship` + `Organization`, `BreadcrumbList`, `WebPage`) con dirección, geo, horarios, identificador del registro y `sameAs` a web y redes.
- Páginas por localidad con resumen en prosa, conteo por denominación, `ItemList` completo y una versión Markdown (`/<provincia>/<localidad>.md`) pensada para crawlers de IA.
- Páginas por tipo (`/tipo/bautista/`, `/tipo/catolica/`, ...) que responden "iglesias X en Argentina" por provincia y localidad.
- `llms.txt` con la descripción del sitio, cómo está organizado, el esquema del dataset y enlaces a las localidades con más iglesias en Markdown.
- `robots.txt` que permite explícitamente GPTBot, ClaudeBot, Google-Extended y PerplexityBot.
- Sitemap index con partes de 10.000 URLs.
- Dataset completo en `/datos/iglesias.json` con CORS abierto.

## Regenerar datos

```bash
python3 -I scripts/normalizar.py data/raw/registro-culto-export.csv data/iglesias.json
python3 -I scripts/enriquecer_osm.py data/raw/osm-place-of-worship.json data/iglesias.json
python3 -I scripts/denominacion.py data/iglesias.json
python3 -I scripts/geocodificar.py data/iglesias.json data/geo.json   # lento: una hora aprox.
python3 -I scripts/aplicar_geo.py data/iglesias.json data/geo.json
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

Se usa Workers con assets estáticos y no Pages porque el sitio tiene unas 47.000 archivos y Pages corta en 20.000. La URL pública se configura con `SITE_URL` al hacer el build (afecta canonical, sitemap, llms.txt y JSON-LD).

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
