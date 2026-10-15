#!/usr/bin/env python3
"""Carga data/<pais>/iglesias/*.json en la tabla `iglesias` de D1 usando la API HTTP de Cloudflare.

Uso: python3 -I scripts/comunes/cargar_d1.py data/ar
Requiere CLOUDFLARE_API_TOKEN, CLOUDFLARE_ACCOUNT_ID y D1_DATABASE_ID en el entorno (o el id en sitio/wrangler.toml).
Borra las fichas del país y las vuelve a insertar, así D1 queda igual que el repo. GitHub es la fuente de verdad.
"""
import json, os, re, sys, time, urllib.request
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from datos import cargar

FILAS_POR_INSERT = 40          # D1 limita el tamaño de cada sentencia (~100 KB)
INSERTS_POR_PEDIDO = 25        # varias sentencias por request HTTP
def q(s): return "'" + str(s).replace("'", "''") + "'"

def db_id():
    if os.environ.get('D1_DATABASE_ID'): return os.environ['D1_DATABASE_ID']
    m = re.search(r'database_id\s*=\s*"([0-9a-f-]+)"', open('sitio/wrangler.toml').read()); return m.group(1)

def ejecutar(sql):
    url = f"https://api.cloudflare.com/client/v4/accounts/{os.environ['CLOUDFLARE_ACCOUNT_ID']}/d1/database/{db_id()}/query"
    req = urllib.request.Request(url, data=json.dumps({'sql': sql}).encode(), headers={'Authorization': f"Bearer {os.environ['CLOUDFLARE_API_TOKEN']}", 'Content-Type': 'application/json'})
    for intento in range(4):
        try:
            r = json.load(urllib.request.urlopen(req, timeout=120))
            if r.get('success'): return r
            print(r.get('errors'), file=sys.stderr); sys.exit(1)
        except urllib.error.HTTPError as e:
            cuerpo = e.read().decode()[:500]
            if e.code in (429, 500, 502, 503, 504): print('HTTP', e.code, 'reintento', intento, file=sys.stderr); time.sleep(5 * (intento + 1)); continue
            print('HTTP', e.code, cuerpo, file=sys.stderr); sys.exit(1)
    sys.exit(1)

def main(carpeta):
    pais = os.path.basename(carpeta.rstrip('/'))
    ig = cargar(carpeta); print(f'{len(ig)} fichas de {pais}', file=sys.stderr)
    ejecutar(f"DELETE FROM iglesias WHERE pais_slug = {q(pais)};")
    inserts = []
    for k in range(0, len(ig), FILAS_POR_INSERT):
        filas = ','.join(f"({q(i['pais_slug'])},{q(i['slug'])},{q(i['provincia_slug'])},{q(i['localidad_slug'])},{q(i['nombre'])},{q(json.dumps(i, ensure_ascii=False))})" for i in ig[k:k+FILAS_POR_INSERT])
        inserts.append(f"INSERT OR REPLACE INTO iglesias (pais_slug, slug, provincia_slug, localidad_slug, nombre, datos) VALUES {filas};")
    for k in range(0, len(inserts), INSERTS_POR_PEDIDO):
        ejecutar('\n'.join(inserts[k:k+INSERTS_POR_PEDIDO]))
        print(f'{min((k+INSERTS_POR_PEDIDO)*FILAS_POR_INSERT, len(ig))}/{len(ig)}', file=sys.stderr)
    n = ejecutar(f"SELECT count(*) AS n FROM iglesias WHERE pais_slug = {q(pais)};")['result'][0]['results'][0]['n']
    print(f'listo: {n} filas de {pais} en D1', file=sys.stderr)

if __name__ == '__main__': main(sys.argv[1])
