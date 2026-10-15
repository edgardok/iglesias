#!/usr/bin/env python3
"""Aplica data/geo.json sobre data/iglesias.json (solo fichas sin coordenadas)."""
import json, sys
import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', 'comunes'))
from datos import cargar, guardar
ig = cargar(sys.argv[1]); geo = json.load(open(sys.argv[2], encoding='utf-8')); n = 0
for i in ig:
    g = geo.get(i['slug'])
    if g and not i.get('lat'): i['lat'] = round(g['lat'], 6); i['lon'] = round(g['lon'], 6); i['geo_fuente'] = 'georef (normalizador de direcciones, aproximado)'; n += 1
guardar(sys.argv[1], ig); print(f'{n} fichas con coordenadas nuevas')
