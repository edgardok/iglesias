#!/usr/bin/env python3
"""Aplica data/geo.json sobre data/iglesias.json (solo fichas sin coordenadas)."""
import json, sys
ig = json.load(open(sys.argv[1], encoding='utf-8')); geo = json.load(open(sys.argv[2], encoding='utf-8')); n = 0
for i in ig:
    g = geo.get(i['slug'])
    if g and not i.get('lat'): i['lat'] = round(g['lat'], 6); i['lon'] = round(g['lon'], 6); i['geo_fuente'] = 'georef (normalizador de direcciones, aproximado)'; n += 1
json.dump(ig, open(sys.argv[1], 'w', encoding='utf-8'), ensure_ascii=False, indent=0); print(f'{n} fichas con coordenadas nuevas')
