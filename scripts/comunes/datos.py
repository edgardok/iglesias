#!/usr/bin/env python3
"""Lectura y escritura del dataset de un país, partido por región en data/<iso>/iglesias/<region_slug>.json.

Uso desde otros scripts:
    from datos import cargar, guardar
    iglesias = cargar('data/ar')      # lista única con todas las fichas del país
    guardar('data/ar', iglesias)      # reescribe un archivo por región (y borra los que quedaron vacíos)
"""
import json, os, glob, sys

def cargar(carpeta_pais):
    out = []
    for ruta in sorted(glob.glob(os.path.join(carpeta_pais, 'iglesias', '*.json'))):
        out += json.load(open(ruta, encoding='utf-8'))
    return out

def guardar(carpeta_pais, iglesias):
    carpeta = os.path.join(carpeta_pais, 'iglesias'); os.makedirs(carpeta, exist_ok=True)
    por_region = {}
    for i in iglesias: por_region.setdefault(i['provincia_slug'], []).append(i)
    for ruta in glob.glob(os.path.join(carpeta, '*.json')):
        if os.path.basename(ruta)[:-5] not in por_region: os.remove(ruta)
    for slug, lista in por_region.items():
        lista.sort(key=lambda i: i['slug'])
        json.dump(lista, open(os.path.join(carpeta, f'{slug}.json'), 'w', encoding='utf-8'), ensure_ascii=False, indent=0)
    return len(por_region)

if __name__ == '__main__':
    # Migración: python3 -I scripts/comunes/datos.py data/ar  (parte data/ar/iglesias.json y lo borra)
    carpeta = sys.argv[1]; viejo = os.path.join(carpeta, 'iglesias.json')
    ig = json.load(open(viejo, encoding='utf-8')); n = guardar(carpeta, ig); os.remove(viejo)
    print(f'{len(ig)} fichas en {n} archivos en {carpeta}/iglesias/')
