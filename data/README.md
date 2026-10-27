# Datos por país

Una carpeta por país, nombrada con su código ISO 3166-1 en minúsculas.

```
data/<iso>/
  raw/          fuentes tal como se descargaron; no se editan
  iglesias/     dataset normalizado del país, un archivo por región (lo que publica el sitio; ninguno debe superar 20 MB)
  fuentes.json  de dónde salió cada dato: organismo, URL, licencia, fecha, script, limitaciones
  geo.json      coordenadas obtenidas por geocodificación (si aplica)
```

El sitio carga todos los `data/*/iglesias.json` y muestra `fuentes.json` en la página de fuentes de cada país.

`data/_archivo/<iso>/` guarda fichas que no se publican porque quedan fuera del alcance actual (hoy: España y Estados Unidos, que quedan fuera de América Latina). Tienen la misma estructura que `data/<iso>/` y se vuelven a publicar moviéndolas de vuelta; no se cargan en D1 ni en el sitio.

Para sumar un país: crear la carpeta, bajar las fuentes a `raw/`, escribir los scripts en `scripts/<iso>/`
(los comunes como OpenStreetMap y denominaciones están en `scripts/comunes/`), y documentar todo en `fuentes.json`.

| País | Estado | Fichas | Fuentes principales |
| --- | --- | --- | --- |
| Argentina (`ar`) | publicado | 32.745 | Registro Nacional de Cultos, OpenStreetMap, georef, federaciones |
| Brasil (`br`) | semilla, en portugués | 10.758 | EncuentraIglesias.com (casi sin ubicación) |
| Chile (`cl`) | semilla | 967 | EncuentraIglesias.com |
| Colombia (`co`) | semilla | 1.165 | EncuentraIglesias.com, FIBEC; pendiente el registro del Ministerio del Interior |
| México (`mx`) | semilla | 2.693 | EncuentraIglesias.com |
| Perú (`pe`) | semilla | 1.189 | EncuentraIglesias.com |

Archivadas (no publicadas): España 2.552 (`_archivo/es`) y Estados Unidos 39.984 (`_archivo/us`).
