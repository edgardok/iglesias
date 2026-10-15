#!/usr/bin/env python3
"""Normaliza el CSV del Registro Nacional de Cultos a data/iglesias.json.

Uso: python3 -I scripts/normalizar.py data/raw/registro-culto-export.csv data/iglesias.json
"""
import csv, json, re, sys, unicodedata, collections

PROV_ALIAS = {
    'tucuman': 'Tucumán',
    'ciudad autonoma de buenos aires': 'Ciudad Autónoma de Buenos Aires',
}
PROV_SLUG_FIX = {'ciudad-autonoma-de-buenos-aires': 'caba'}

def slugify(s):
    s = unicodedata.normalize('NFKD', s).encode('ascii', 'ignore').decode()
    s = re.sub(r'[^a-zA-Z0-9]+', '-', s).strip('-').lower()
    return s or 'sin-datos'

def titulo(s):
    s = re.sub(r'\s+', ' ', s).strip()
    if not s: return s
    small = {'de', 'del', 'la', 'las', 'los', 'el', 'y', 'en', 'a', 'al', 'por', 'para', 'con', 'sud'}
    out = []
    for i, w in enumerate(s.lower().split(' ')):
        if re.fullmatch(r'[ivxlc]+', w) and len(w) <= 4: out.append(w.upper()); continue
        if re.fullmatch(r'\d+[ºª°]?', w): out.append(w); continue
        out.append(w if (w in small and i > 0) else w.capitalize())
    return ' '.join(out)

def partir_nombre(n):
    n = re.sub(r'\s+', ' ', n).strip()
    m = re.match(r'^(.*?)\s*[-–]\s*FILIAL\s*(?:N[º°]?\s*)?(\d*)\s*$', n, re.I)
    if m:
        return m.group(1).strip(' -–'), (m.group(2) or None)
    return n, None

def limpiar_dir(d):
    d = re.sub(r'\s+', ' ', d).strip(' ,-')
    d = re.sub(r'\bS/N[º°]?\b', 's/n', d, flags=re.I)
    return d

def main(src, dst):
    rows = list(csv.reader(open(src, encoding='utf-8', errors='replace')))
    out, vistos = [], collections.Counter()
    for r in rows:
        if len(r) < 5: continue
        nombre, direccion, localidad, provincia, ci = [c.strip() for c in r]
        if not nombre: continue
        entidad, filial = partir_nombre(nombre)
        provincia = PROV_ALIAS.get(slugify(provincia).replace('-', ' '), titulo(provincia)) if provincia else ''
        prov_slug = PROV_SLUG_FIX.get(slugify(provincia), slugify(provincia)) if provincia else 'sin-provincia'
        if slugify(localidad) == 'capital-federal': localidad = 'Ciudad de Buenos Aires'
        loc = titulo(localidad) or 'Sin localidad'
        base = slugify(f"{entidad} {filial or ''} {loc}")
        vistos[base] += 1
        slug = base if vistos[base] == 1 else f"{base}-{vistos[base]}"
        out.append({
            'slug': slug,
            'nombre': titulo(entidad) + (f' - Filial {filial}' if filial else ''),
            'entidad': titulo(entidad),
            'entidad_slug': slugify(entidad),
            'filial': filial,
            'direccion': limpiar_dir(direccion),
            'localidad': loc,
            'localidad_slug': slugify(loc),
            'provincia': provincia or 'Sin provincia',
            'provincia_slug': prov_slug,
            'registro_ci': ci or None,
            'fuente': 'Registro Nacional de Cultos (Cancillería Argentina)',
            # Campos que completan las iglesias o el enriquecimiento:
            'web': None, 'facebook': None, 'instagram': None, 'google_maps': None,
            'telefono': None, 'email': None, 'horarios': None, 'lat': None, 'lon': None,
            'reclamada': False,
        })
    json.dump(out, open(dst, 'w', encoding='utf-8'), ensure_ascii=False, indent=0)
    print(f'{len(out)} registros -> {dst}')
    print('provincias:', sorted({o["provincia"] for o in out}))

if __name__ == '__main__':
    main(sys.argv[1], sys.argv[2])
