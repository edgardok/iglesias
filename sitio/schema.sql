-- Solicitudes del formulario "Sumar mi iglesia"
CREATE TABLE IF NOT EXISTS solicitudes (
  id TEXT PRIMARY KEY,
  creado TEXT NOT NULL,
  estado TEXT NOT NULL DEFAULT 'pendiente',   -- pendiente | aprobada | rechazada | revisar
  ip_hash TEXT,
  datos TEXT NOT NULL,                        -- JSON con los campos del formulario
  resolucion TEXT,                            -- JSON con lo que decidió el agente
  resuelto TEXT
);
CREATE INDEX IF NOT EXISTS solicitudes_estado ON solicitudes (estado, creado);

-- Fichas de iglesias: copia de data/<pais>/iglesias/*.json que el Worker consulta para renderizar.
-- Se recarga en cada deploy con scripts/comunes/cargar_d1.py. GitHub es la fuente de verdad.
CREATE TABLE IF NOT EXISTS iglesias (
  pais_slug TEXT NOT NULL,
  slug TEXT NOT NULL,
  provincia_slug TEXT NOT NULL,
  localidad_slug TEXT NOT NULL,
  nombre TEXT NOT NULL,
  datos TEXT NOT NULL,                        -- la ficha completa en JSON
  PRIMARY KEY (pais_slug, slug)
);
CREATE INDEX IF NOT EXISTS iglesias_localidad ON iglesias (pais_slug, provincia_slug, localidad_slug, nombre);
