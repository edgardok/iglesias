#!/usr/bin/env python3
"""Actualiza en D1 solo las coordenadas (lat, lon y los campos lat/lon/geo_fuente del JSON) de las fichas que las ganaron.

Escribe menos que recargar todo el país: una fila por ficha cambiada. El plan gratuito de D1 permite 100.000 filas
escritas por día (los índices cuentan), así que ante un error de cuota el script se detiene y avisa dónde quedó.

Uso: python3 -I scripts/comunes/cargar_geo_d1.py data/mx [data/pe ...]
Requiere CLOUDFLARE_API_TOKEN y CLOUDFLARE_ACCOUNT_ID.
"""
import json, os, re, sys, time, urllib.request, urllib.error
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from datos import cargar

LOTE = 150
def q(s): return "'" + str(s).replace("'", "''") + "'"

def db_id():
    return re.search(r'database_id\s*=\s*"([0-9a-f-]+)"', open('sitio/wrangler.toml').read()).group(1)

def ejecutar(sql):
    url = f"https://api.cloudflare.com/client/v4/accounts/{os.environ['CLOUDFLARE_ACCOUNT_ID']}/d1/database/{db_id()}/query"
    req = urllib.request.Request(url, data=json.dumps({'sql': sql}).encode(), headers={'Authorization': f"Bearer {os.environ['CLOUDFLARE_API_TOKEN']}", 'Content-Type': 'application/json'})
    for intento in range(4):
        try:
            r = json.load(urllib.request.urlopen(req, timeout=120))
            if r.get('success'): return r
            print(r.get('errors'), file=sys.stderr); sys.exit(2)
        except urllib.error.HTTPError as e:
            cuerpo = e.read().decode()[:400]
            if e.code in (429, 500, 502, 503, 504) and 'quota' not in cuerpo.lower() and 'limit' not in cuerpo.lower(): time.sleep(5 * (intento + 1)); continue
            print('HTTP', e.code, cuerpo, file=sys.stderr); sys.exit(2)
    sys.exit(2)

def main(carpeta):
    pais = os.path.basename(carpeta.rstrip('/'))
    conc = [i for i in cargar(carpeta) if i.get('lat') and (i.get('geo_fuente') or '').startswith('GeoNames')]
    print(f'{pais}: {len(conc)} fichas con coordenadas de GeoNames para actualizar', file=sys.stderr)
    for k in range(0, len(conc), LOTE):
        lote = conc[k:k + LOTE]
        valores = ','.join(f"({q(i['pais_slug'])},{q(i['slug'])},{i['lat']!r},{i['lon']!r},{q(i['geo_fuente'])})" for i in lote)
        ejecutar(f"UPDATE iglesias SET lat = v.column3, lon = v.column4, datos = json_set(datos, '$.lat', v.column3, '$.lon', v.column4, '$.geo_fuente', v.column5) "
                 f"FROM (VALUES {valores}) AS v WHERE iglesias.pais_slug = v.column1 AND iglesias.slug = v.column2;")
        if (k // LOTE) % 10 == 9 or k + LOTE >= len(conc): print(f'  {min(k + LOTE, len(conc))}/{len(conc)}', file=sys.stderr)
    n = ejecutar(f"SELECT count(*) AS n FROM iglesias WHERE pais_slug = {q(pais)} AND lat IS NOT NULL;")['result'][0]['results'][0]['n']
    print(f'listo: {pais} tiene {n} filas con coordenadas en D1', file=sys.stderr)

if __name__ == '__main__':
    for c in sys.argv[1:]: main(c)
