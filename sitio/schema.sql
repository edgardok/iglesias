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
