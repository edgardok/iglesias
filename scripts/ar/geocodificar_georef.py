#!/usr/bin/env python3
"""Geocodifica las fichas sin coordenadas con la API georef (normalizador de direcciones del Estado).

Solo acepta resultados filtrados por provincia + localidad censal, o provincia + departamento. Sin filtro
georef puede ubicar la calle en otro partido, así que preferimos no tener coordenadas a tenerlas mal.
Escribe data/geo.json {slug: {lat, lon, direccion_normalizada, filtro}}. Se aplica con aplicar_geo.py.
Uso: python3 -I scripts/geocodificar.py data/iglesias.json data/geo.json
"""
import json, re, sys, time, urllib.request, urllib.error
from concurrent.futures import ThreadPoolExecutor

LOTE = 100
def limpiar(d):
    d = re.sub(r'\b(manzana|mza?\.?|lote|parcela|casa|dpto\.?|depto\.?|piso|local|galpon|fracc\.?|barrio|b[º°]|entre|e/)\b.*$', '', d, flags=re.I)
    d = re.sub(r'\bN[º°]?\s*(?=\d)', '', d); d = re.sub(r'\s+', ' ', d).strip(' ,-.')
    return d

def pedir(items):
    body = {'direcciones': items}
    for intento in range(3):
        try:
            req = urllib.request.Request('https://apis.datos.gob.ar/georef/api/direcciones', data=json.dumps(body).encode(), headers={'Content-Type': 'application/json', 'User-Agent': 'iglesias-ar/0.1'})
            return json.load(urllib.request.urlopen(req, timeout=180))['resultados']
        except urllib.error.HTTPError as e:
            if e.code == 400:
                if len(items) == 1: return [{'direcciones': []}]
                m = len(items) // 2; return pedir(items[:m]) + pedir(items[m:])
            print('HTTP', e.code, 'reintento', intento, file=sys.stderr); time.sleep(10 * (intento + 1))
        except Exception as e:
            print('error', e, 'reintento', intento, file=sys.stderr); time.sleep(10 * (intento + 1))
    return [{'direcciones': []} for _ in items]

def pasada(pend, geo, filtro, dst):
    lotes = [pend[k:k+LOTE] for k in range(0, len(pend), LOTE)]
    def trabajo(lote):
        items = [{'direccion': limpiar(i['direccion']), 'provincia': i['provincia'], filtro: i['localidad'], 'max': 1, 'campos': 'estandar'} for i in lote]
        return list(zip(lote, pedir(items)))
    hechos = 0
    with ThreadPoolExecutor(max_workers=4) as ex:
        for res in ex.map(trabajo, lotes):
            for i, r in res:
                ds = r.get('direcciones') or []
                u = ds[0].get('ubicacion') if ds else None
                if u and u.get('lat'): geo[i['slug']] = {'lat': u['lat'], 'lon': u['lon'], 'direccion_normalizada': ds[0].get('nomenclatura'), 'filtro': filtro}
            hechos += len(res)
            if hechos % (LOTE * 5) == 0 or hechos == len(pend):
                json.dump(geo, open(dst, 'w', encoding='utf-8'), ensure_ascii=False)
                print(f'[{filtro}] {hechos}/{len(pend)} -> {len(geo)} geocodificadas', file=sys.stderr)
    json.dump(geo, open(dst, 'w', encoding='utf-8'), ensure_ascii=False)

def main(src, dst):
    ig = json.load(open(src, encoding='utf-8'))
    try: geo = json.load(open(dst, encoding='utf-8'))
    except Exception: geo = {}
    def pend(): return [i for i in ig if not i.get('lat') and i['slug'] not in geo and i['direccion'] and re.search(r'\d', i['direccion']) and i['provincia'] != 'Sin provincia' and i['localidad'] != 'Sin localidad']
    p = pend(); print(f'{len(p)} fichas a geocodificar', file=sys.stderr)
    pasada([i for i in p if i['localidad'] != 'Ciudad de Buenos Aires'], geo, 'localidad_censal', dst)
    pasada([i for i in pend() if i['localidad'] != 'Ciudad de Buenos Aires'], geo, 'departamento', dst)
    # CABA: la provincia ya es el filtro suficiente
    caba = [i for i in pend() if i['localidad'] == 'Ciudad de Buenos Aires']
    for k in range(0, len(caba), LOTE):
        lote = caba[k:k+LOTE]
        for i, r in zip(lote, pedir([{'direccion': limpiar(i['direccion']), 'provincia': 'Ciudad Autónoma de Buenos Aires', 'max': 1, 'campos': 'estandar'} for i in lote])):
            ds = r.get('direcciones') or []; u = ds[0].get('ubicacion') if ds else None
            if u and u.get('lat'): geo[i['slug']] = {'lat': u['lat'], 'lon': u['lon'], 'direccion_normalizada': ds[0].get('nomenclatura'), 'filtro': 'provincia'}
        json.dump(geo, open(dst, 'w', encoding='utf-8'), ensure_ascii=False)
    print(f'listo: {len(geo)} fichas geocodificadas', file=sys.stderr)

if __name__ == '__main__': main(sys.argv[1], sys.argv[2])
