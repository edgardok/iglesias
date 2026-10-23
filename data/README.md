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

Para sumar un país: crear la carpeta, bajar las fuentes a `raw/`, escribir los scripts en `scripts/<iso>/`
(los comunes como OpenStreetMap y denominaciones están en `scripts/comunes/`), y documentar todo en `fuentes.json`.

| País | Estado | Fichas | Fuentes principales |
| --- | --- | --- | --- |
| Argentina (`ar`) | publicado | 32.745 | Registro Nacional de Cultos, OpenStreetMap, georef, federaciones |
| Brasil (`br`) | semilla | 10.758 | EncuentraIglesias.com (casi sin ubicación) |
| Chile (`cl`) | semilla | 967 | EncuentraIglesias.com |
| Colombia (`co`) | semilla | 1.165 | EncuentraIglesias.com, FIBEC; pendiente el registro del Ministerio del Interior |
| México (`mx`) | semilla | 2.693 | EncuentraIglesias.com |
| Perú (`pe`) | semilla | 1.189 | EncuentraIglesias.com |
| España (`es`) | semilla, fuera de América Latina | 2.552 | EncuentraIglesias.com |
| Estados Unidos (`us`) | semilla, fuera de América Latina | 39.984 | EncuentraIglesias.com |
