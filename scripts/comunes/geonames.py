#!/usr/bin/env python3
"""Pone coordenadas aproximadas (centro de la localidad) a las fichas sin coordenadas, usando GeoNames.

Fuente: GeoNames cities500 (https://download.geonames.org/export/dump/), licencia CC BY 4.0. Hay que atribuirla.
Se baja a data/_geonames/ (ignorado por git):
    curl -L -o data/_geonames/cities500.zip https://download.geonames.org/export/dump/cities500.zip
    curl -L -o data/_geonames/admin1CodesASCII.txt https://download.geonames.org/export/dump/admin1CodesASCII.txt
    (y descomprimir cities500.txt en la misma carpeta)

Cómo ubica: busca el nombre de la localidad (sin tildes) entre las ciudades del país.
  - Si hay una sola candidata, la usa.
  - Si hay varias, desempata con la región: el mapa región-nuestra -> región-GeoNames se aprende de las localidades
    que tienen una sola candidata (voto mayoritario). Sin región conocida, las ambiguas se saltean.
No pisa coordenadas existentes. Marca geo_fuente = 'GeoNames: centro de la localidad (aproximado)'.

Uso: python3 -I scripts/comunes/geonames.py <iso> [<iso> ...]
"""
import collections, os, re, sys, unicodedata
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from datos import cargar, guardar

RAIZ = os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', '..', 'data')
GEO_FUENTE = 'GeoNames: centro de la localidad (aproximado)'
PAIS = {'ar': 'AR', 'br': 'BR', 'cl': 'CL', 'co': 'CO', 'es': 'ES', 'mx': 'MX', 'pe': 'PE', 'us': 'US'}

def slug(s):
    s = unicodedata.normalize('NFKD', s or '').encode('ascii', 'ignore').decode()
    return re.sub(r'[^a-zA-Z0-9]+', '-', s).strip('-').lower()

def cargar_ciudades(cc):
    por_nombre = collections.defaultdict(dict)  # slug -> {geonameid: (lat, lon, admin1, pob)}
    with open(os.path.join(RAIZ, '_geonames', 'cities500.txt'), encoding='utf-8') as f:
        for linea in f:
            c = linea.rstrip('\n').split('\t')
            if len(c) < 15 or c[8] != cc or c[6] != 'P': continue
            reg = (c[10], float(c[4]), float(c[5]), int(c[14] or 0))
            for nombre in {slug(c[1]), slug(c[2])}:
                if nombre: por_nombre[nombre][c[0]] = reg
    return por_nombre

def procesar(iso):
    carpeta = os.path.join(RAIZ, iso)
    ig = cargar(carpeta); por_nombre = cargar_ciudades(PAIS[iso])
    cand = lambda i: list(por_nombre.get(i['localidad_slug'], {}).values())
    # 1) aprender región nuestra -> admin1 de GeoNames con las localidades de candidata única
    votos = collections.defaultdict(collections.Counter)
    for i in ig:
        if i['localidad'] == 'Sin localidad' or i.get('lat') or i['provincia_slug'].startswith('sin-'): continue
        c = cand(i)
        if len(c) == 1: votos[i['provincia_slug']][c[0][0]] += 1
    mapa = {}
    for r, cnt in votos.items():
        a, n = cnt.most_common(1)[0]
        if n >= 3 and n / sum(cnt.values()) >= 0.6: mapa[r] = a
    # centro de cada región nuestra = mediana de las localidades de candidata única que caen en ella
    puntos = collections.defaultdict(list)
    for i in ig:
        if i['localidad'] == 'Sin localidad' or i['provincia_slug'].startswith('sin-'): continue
        c = cand(i)
        if len(c) == 1: puntos[i['provincia_slug']].append((c[0][1], c[0][2]))
    centro = {}
    for r, l in puntos.items():
        if len(l) >= 5: centro[r] = (sorted(x[0] for x in l)[len(l) // 2], sorted(x[1] for x in l)[len(l) // 2])
    import math
    km = lambda a, b: math.hypot((a[0] - b[0]) * 111, (a[1] - b[1]) * 111 * math.cos(math.radians(a[0])))
    RADIO = {'us': 1800, 'br': 1500, 'mx': 900, 'pe': 700, 'cl': 900, 'co': 600, 'es': 450, 'ar': 1000}[iso]
    # 2) ubicar
    stats = collections.Counter(); nuevas = 0
    for i in ig:
        if i.get('lat'): stats['ya tenía'] += 1; continue
        if i['localidad'] == 'Sin localidad': stats['sin localidad'] += 1; continue
        if i['localidad_slug'] == i['provincia_slug']: stats['localidad = región (se omite)'] += 1; continue
        c = cand(i)
        if not c: stats['no está en GeoNames'] += 1; continue
        elegido = None
        if len(c) == 1: elegido = c[0]
        else:
            a = mapa.get(i['provincia_slug'])
            if a:
                m = [x for x in c if x[0] == a]
                if m: elegido = max(m, key=lambda x: x[3])
            if not elegido: stats['ambigua sin región'] += 1; continue
        ctr = centro.get(i['provincia_slug'])
        if ctr and km(ctr, (elegido[1], elegido[2])) > RADIO: stats['lejos de su región (se omite)'] += 1; continue
        i['lat'], i['lon'], i['geo_fuente'] = round(elegido[1], 5), round(elegido[2], 5), GEO_FUENTE
        nuevas += 1; stats['ubicada'] += 1
    guardar(carpeta, ig)
    print(f'{iso}: +{nuevas} con coordenadas de {len(ig)} | {dict(stats)} | regiones mapeadas: {len(mapa)}')
    return nuevas

if __name__ == '__main__':
    for iso in sys.argv[1:]: procesar(iso)
