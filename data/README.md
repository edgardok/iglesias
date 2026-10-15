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
|---|---|---|---|
| Argentina (`ar`) | publicado | 32.706 | Registro Nacional de Cultos, OpenStreetMap, georef |
| Colombia (`co`) | semilla | 1.284 | CSV recopilado de directorios web (EncuentraIglesias, FIBEC); pendiente el registro del Ministerio del Interior |
