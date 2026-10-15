# Iglesias de América Latina: directorio abierto

Directorio estático con una URL por templo, pensado para que buscadores y asistentes de IA puedan responder
"qué iglesias hay en tal localidad". Miles de iglesias existen solo en Facebook, Instagram o WhatsApp, que ni
Google ni los modelos de lenguaje pueden leer. Acá juntamos los datos públicos de cada país, los normalizamos
y los publicamos con datos estructurados, documentando de dónde sale cada dato.

Alcance: América Latina, país por país. Hoy está Argentina (37.155 fichas). Cada país se suma cuando hay una
fuente pública confiable.

## Estructura

```
data/<iso>/            un país por carpeta (código ISO 3166-1 en minúsculas)
  raw/                 fuentes tal como se bajaron; no se editan
  iglesias/<region>.json  dataset normalizado, un archivo por región (límite 20 MB cada uno)
  fuentes.json         de dónde salió cada dato: organismo, URL, licencia, fecha, script, limitaciones
  geo.json             coordenadas obtenidas por geocodificación (si aplica)
scripts/<iso>/         scripts específicos del país (parsear su registro, geocodificar con su API)
scripts/comunes/       scripts que sirven para todos: OpenStreetMap, inferencia de denominación
sitio/                 Astro (estático) + Worker de Cloudflare para el formulario
  src/pages/           inicio, países, /<pais>/ por región, localidades (HTML y .md), tipo, fuentes, ficha por iglesia, formulario, llms.txt, sitemaps, datos
  functions/api/       handlers del formulario (Turnstile + D1) y del endpoint para el agente
  worker/index.ts      enruta /api/* a los handlers y sirve el resto como assets
  agente/procesar.ts   agente con Claude que revisa las solicitudes y actualiza data/<pais>/iglesias/<region>.json
```

Detalle de los datos y cómo sumar un país: [data/README.md](data/README.md).

## URLs

- `/<pais>/` país por región · `/<pais>/<region>/` · `/<pais>/<region>/<localidad>/` y `.md`
- `/<pais>/iglesia/<slug>/` ficha permanente de cada iglesia
- `/<pais>/tipo/<denominacion>/` · `/<pais>/fuentes/`
- `/fuentes/`, `/datos/`, `/datos/iglesias.json`, `/datos/<pais>.json`, `/llms.txt`, `/sitemap.xml`

## Optimización para buscadores y LLMs

- Una URL permanente por iglesia con un párrafo en prosa que resume lo que se sabe de ella y JSON-LD (`PlaceOfWorship` + `Organization`, `BreadcrumbList`, `WebPage`) con dirección, geo, horarios, identificador del registro y `sameAs` a web y redes.
- Páginas por localidad con resumen en prosa, conteo por denominación, `ItemList` completo y una versión Markdown pensada para crawlers de IA.
- Páginas por tipo que responden "iglesias X en <país>" por región y localidad.
- `llms.txt` con la descripción del sitio, cómo está organizado, el esquema del dataset y las localidades con más iglesias en Markdown.
- `robots.txt` que permite explícitamente GPTBot, ClaudeBot, Google-Extended y PerplexityBot.
- Sitemap index con partes de 10.000 URLs. Dataset completo y por país con CORS abierto.
- Página de fuentes por país generada desde `fuentes.json`, con enlace al archivo crudo y al script.

## Principios sobre los datos

- Solo fuentes públicas o con licencia abierta. No se raspan Facebook, Instagram ni Google Maps: las iglesias pegan sus enlaces en el formulario.
- Preferimos no tener un dato a tenerlo mal (por ejemplo, no se publican coordenadas sin confirmar la localidad).
- Todo lo que aportan las iglesias se publica bajo ODbL, igual que el resto.

## Regenerar datos (Argentina)

```bash
python3 -I scripts/ar/registro_cultos.py data/ar/raw/registro-culto-export.csv data/ar
python3 -I scripts/comunes/enriquecer_osm.py data/ar/raw/osm-place-of-worship.json data/ar
python3 -I scripts/comunes/denominacion.py data/ar
python3 -I scripts/ar/geocodificar_georef.py data/ar data/ar/geo.json   # lento: una hora aprox.
python3 -I scripts/ar/aplicar_geo.py data/ar data/ar/geo.json
```

## Sitio

```bash
cd sitio && npm install && npm run build && npm run dev
```

## Desplegar en Cloudflare (gratis)

Conectado por GitHub: Workers & Pages → Import a repository → este repo. Root directory `sitio`, build `npm run build`,
deploy `npx wrangler deploy`. Variables de build: `SITE_URL` (URL pública; define canonical, sitemap y JSON-LD) y
`PUBLIC_TURNSTILE_SITE_KEY`.

Después del primer deploy, para que el formulario funcione:

1. `npx wrangler d1 create iglesias-latam`, pegar el id en `sitio/wrangler.toml` y descomentar el bloque D1.
2. `npx wrangler d1 execute iglesias-latam --file=schema.sql --remote`
3. Crear un sitio en Turnstile y cargar `npx wrangler secret put TURNSTILE_SECRET_KEY` y `npx wrangler secret put AGENTE_TOKEN`.

Se usa Workers con assets estáticos y no Pages porque el sitio tiene unos 48.000 archivos y Pages corta en 20.000.

## Agente

```bash
cd sitio
npx tsx agente/procesar.ts --local agente/ejemplo-solicitudes.json --dry-run   # prueba sin tocar nada
API_BASE=https://<worker>.workers.dev AGENTE_TOKEN=... npx tsx agente/procesar.ts
```

Necesita credenciales de la API de Anthropic. El agente escribe en `data/<pais>/iglesias/<region>.json` y marca las
solicitudes; publicar sigue siendo un commit y un deploy hechos por una persona.

## Pendiente

- Más países. Candidatos con registro público: Chile (Registro de Entidades Religiosas), Colombia (Registro Público de Entidades Religiosas del Ministerio del Interior), México (Asociaciones Religiosas de la SEGOB), Perú (Registro de Entidades Religiosas del Ministerio de Justicia), Brasil (CNPJ con CNAE 94.91-0).
- Correr el agente contra solicitudes reales.
- Parroquias católicas de Argentina (guía AICA).
- Email a quien reclama la ficha cuando se publica.
