# Iglesias de América Latina: directorio abierto

Directorio estático de iglesias evangélicas y otras comunidades de fe no católicas, con una URL por templo, pensado para que buscadores y asistentes de IA puedan responder
"qué iglesias hay en tal localidad". Miles de iglesias existen solo en Facebook, Instagram o WhatsApp, que ni
Google ni los modelos de lenguaje pueden leer. Acá juntamos los datos públicos de cada país, los normalizamos
y los publicamos con datos estructurados, documentando de dónde sale cada dato.

Alcance: América Latina, país por país. Hoy hay datos de Argentina (la más completa, con el registro oficial), Colombia, Brasil, Chile, México y Perú, más España y Estados Unidos fuera de América Latina. Salvo Argentina son semillas: casi todo viene de un directorio de terceros, sin dirección ni coordenadas. Cada país se suma cuando hay una
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
sitio/                 Astro con el adaptador de Cloudflare: páginas estáticas + Worker que lee D1
  src/pages/           inicio, países, /<pais>/ por región, tipo, fuentes, formulario, llms.txt, sitemaps, datos (estáticas);
                       fichas de iglesia, localidades (HTML y .md) y /api/* (renderizadas en el Worker desde D1)
  src/lib/datos.ts     lee data/*/iglesias/*.json del disco en el build (solo páginas estáticas)
  src/lib/d1.ts        consultas a D1 para las páginas que corren en el Worker
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

- Preferimos fuentes públicas o con licencia abierta. Donde aún no hay un registro oficial usamos directorios web de terceros, declarados como tales y con el enlace de origen en cada ficha, hasta reemplazarlos. No se raspan Facebook, Instagram ni Google Maps: las iglesias pegan sus enlaces en el formulario.
- Preferimos no tener un dato a tenerlo mal (por ejemplo, no se publican coordenadas sin confirmar la localidad).
- Todo lo que aportan las iglesias se publica bajo ODbL, igual que el resto.

## Regenerar datos

Países con CSV recopilado (Brasil, Chile, México, Perú, España, Estados Unidos; Argentina anexa solo las filas de federaciones):

```bash
python3 -I scripts/comunes/csv_encuentraiglesias.py mx data/mx/raw/churches_Mexico.csv data/mx
python3 -I scripts/comunes/csv_encuentraiglesias.py ar data/ar/raw/churches_Argentina_encuentraiglesias.csv data/ar --anexar --sin-encuentraiglesias
```

Colombia (mismo formato, con ciudades conocidas de Colombia):

```bash
python3 -I scripts/co/csv_inicial.py data/co/raw/churches_colombia.csv data/co
```

Argentina:

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

## Arquitectura en Cloudflare (plan gratuito)

El plan gratuito de Workers permite 20.000 archivos estáticos por Worker, y solo Argentina tendría 42.000 páginas.
Por eso el sitio es híbrido:

- **Estático** (~100 archivos): portada, países, regiones, tipos, fuentes, formulario, sitemaps, llms.txt y los JSON por región.
- **Renderizado en el Worker desde D1**: la ficha de cada iglesia (`/<pais>/iglesia/<slug>/`), las páginas de localidad
  (HTML y `.md`) y la API del formulario. D1 es la base SQLite de Cloudflare; tiene una copia de todas las fichas en la
  tabla `iglesias`. Las respuestas se cachean en el borde (`s-maxage=86400`).
- **GitHub es la fuente de verdad.** D1 es una copia que se recarga con `scripts/comunes/cargar_d1.py` después de cambiar datos.

### Deploy

Conectado por GitHub: cada push a `main` dispara `npm run build` y `npx wrangler deploy` (configurado en `wrangler.toml`,
`[build]`). Root directory del proyecto en Cloudflare: `sitio`.

Cuando cambian los datos de un país, además hay que recargar D1 (una vez, desde cualquier máquina con el token):

```bash
python3 -I scripts/comunes/cargar_d1.py data/ar              # borra y vuelve a cargar el país
python3 -I scripts/comunes/cargar_d1.py data/ar --incremental # solo agrega lo que falta, sin borrar
```

El plan gratuito de D1 permite 100.000 filas escritas por día: cargar de a un país por vez y usar `--incremental` cuando se pueda.

Necesita `CLOUDFLARE_API_TOKEN` y `CLOUDFLARE_ACCOUNT_ID` en el entorno (en este repo se cargan desde `.env`, que no se versiona).

### Configuración ya hecha (una sola vez)

- Base D1 `iglesias` con el esquema de `sitio/schema.sql` (tablas `solicitudes` e `iglesias`).
- Widget de Turnstile `iglesias`; la clave pública está en `sumarse.astro` y la secreta como secreto del Worker.
- Secretos del Worker: `TURNSTILE_SECRET_KEY`, `AGENTE_TOKEN`.

## Agente

```bash
cd sitio
npx tsx agente/procesar.ts --local agente/ejemplo-solicitudes.json --dry-run   # prueba sin tocar nada
API_BASE=https://iglesias.edgardo-krause.workers.dev AGENTE_TOKEN=... npx tsx agente/procesar.ts   # el token está en .env
```

Necesita credenciales de la API de Anthropic. El agente escribe en `data/<pais>/iglesias/<region>.json` y marca las
solicitudes; publicar sigue siendo un commit y un deploy hechos por una persona.

## Pendiente

- Más países. Candidatos con registro público: Chile (Registro de Entidades Religiosas), Colombia (Registro Público de Entidades Religiosas del Ministerio del Interior), México (Asociaciones Religiosas de la SEGOB), Perú (Registro de Entidades Religiosas del Ministerio de Justicia), Brasil (CNPJ con CNAE 94.91-0).
- Correr el agente contra solicitudes reales.
- Email a quien reclama la ficha cuando se publica.
