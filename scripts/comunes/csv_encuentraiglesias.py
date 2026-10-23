#!/usr/bin/env python3
"""Importa un CSV recopilado (formato churches_<pais>.csv) a data/<iso>/iglesias/<region>.json.

Casi todas las filas vienen de EncuentraIglesias.com y no traen ciudad ni región en columnas. Se recuperan del final
de la URL de origen (por ejemplo ".../iglesia/<nombre>-sotuta-yucatan"), usando las listas de scripts/comunes/regiones.py.
Lo que no se puede ubicar queda en "Sin <región>" / "Sin localidad". Se descartan las filas con marcas católicas inequívocas.

Uso:
  python3 -I scripts/comunes/csv_encuentraiglesias.py <iso> <csv> data/<iso> [--anexar] [--sin-encuentraiglesias]
    --anexar               suma a lo que ya hay en data/<iso>/iglesias/ en vez de reemplazarlo
    --sin-encuentraiglesias  omite las filas de EncuentraIglesias.com (deja las de fuentes propias: federaciones, registros)
"""
import csv, os, re, sys, unicodedata, collections
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from datos import cargar, guardar
from regiones import REGIONES, CATOLICAS

def slugify(s):
    s = unicodedata.normalize('NFKD', s or '').encode('ascii', 'ignore').decode()
    return re.sub(r'[^a-zA-Z0-9]+', '-', s).strip('-').lower()

PEQUENAS = {'de', 'del', 'la', 'las', 'los', 'el', 'y', 'en', 'a', 'al', 'do', 'da', 'dos', 'das', 'of', 'the', 'and'}
def titulo(tokens):
    return ' '.join(t if (t in PEQUENAS and i > 0) else t.capitalize() for i, t in enumerate(tokens))

RUIDO = {'iglesia', 'templo', 'capilla', 'oratorio', 'ministerio', 'centro', 'church', 'ns', 'nn', 'sa'}
DENOM = {'Cristiana': 'Evangélica', 'Evangélica': 'Evangélica', 'Pentecostal': 'Pentecostal', 'Bautista': 'Bautista', 'Adventista del Séptimo Día': 'Adventista del Séptimo Día', 'Anglicana': 'Anglicana',
         'Presbiteriana': 'Presbiteriana / Reformada', 'Reformada': 'Presbiteriana / Reformada', 'Metodista': 'Metodista', 'Luterana': 'Luterana', 'Menonita': 'Menonita', 'Ejército de Salvación': 'Ejército de Salvación',
         'Discípulos de Cristo': 'Discípulos de Cristo', 'Iglesia de Dios': 'Iglesia de Dios', 'Múltiples': None}

def es_catolica(nombre):
    n = ' ' + re.sub(r'[^a-z0-9 ]+', ' ', unicodedata.normalize('NFKD', nombre.lower()).encode('ascii', 'ignore').decode()) + ' '
    return any(m in n for m in CATOLICAS)

def sufijo(tokens, tabla):
    """Coincidencia más larga de los últimos tokens con una clave de la tabla -> (nombre, n_tokens) o None."""
    for n in range(min(5, len(tokens)), 0, -1):
        k = tuple(tokens[-n:])
        if k in tabla: return tabla[k], n
    return None

def ubicar(r, cfg):
    """(localidad, región) a partir del final de la URL, o (None, None)."""
    m = re.search(r'/iglesia/(.+?)(?:-(\d+))?$', r.get('source_url', ''))
    if not m: return None, None
    slug, ns = m.group(1), slugify(r['name'])
    if not slug.startswith(ns): return None, None
    t = [x for x in slug[len(ns):].strip('-').split('-') if x]
    if not t: return None, None
    marcas, regiones, abrev = cfg['marcas'], cfg['regiones'], cfg['abrev']
    def quitar_marcas(tt):
        quitado = False
        while True:
            for mk in marcas + [('chile',)] if cfg['pais'] == 'Chile' else marcas:
                if len(tt) >= len(mk) and tuple(tt[-len(mk):]) == mk and len(tt) > len(mk) - 1:
                    tt = tt[:-len(mk)]; quitado = True; break
            else: return tt, quitado
    # 1) coincidencia con la región sin quitar nada (estado-de-mexico, ciudad-de-mexico)
    hit = sufijo(t, regiones)
    if hit and not (len(t) == hit[1] and hit[0] and t[-1] in {x for mk in marcas for x in mk} and len(t) == 1):
        region, n = hit; loc = t[:-n]
    else:
        t2, quitado = quitar_marcas(t)
        if quitado and t2 and t2[-1] in abrev: region, loc = abrev[t2[-1]], t2[:-1]
        else:
            hit = sufijo(t2, regiones)
            if hit: region, n = hit; loc = t2[:-n]
            else: region, loc = None, t2
    while loc and loc[-1] in RUIDO: loc = loc[:-1]
    if loc and (loc[0] in RUIDO and len(loc) == 1): loc = []
    if len(loc) > 5 or any(x.isdigit() for x in loc): loc = []
    localidad = titulo(loc) if loc else None
    if not localidad and region and cfg['region_como_localidad']: localidad = region
    if not localidad and not region: return None, None
    return localidad, region

def main(iso, src, dst, anexar=False, sin_ei=False):
    cfg = REGIONES[iso]; pais = cfg['pais']
    existentes = cargar(dst) if anexar else []
    vistos = {i['slug'] for i in existentes}
    ya = {(i['nombre'], i['fuente']) for i in existentes}  # para que --anexar sea idempotente
    out, omitidas_cat, omitidas_ei = [], 0, 0
    for r in csv.DictReader(open(src, encoding='utf-8')):
        nombre = re.sub(r'\s+', ' ', r['name']).strip()
        if not nombre or nombre.lower().startswith(('directorio ', 'registro nacional', 'registro público', 'registro publico')): continue  # filas que describen un directorio u organismo, no una iglesia
        if sin_ei and r['source'] == 'EncuentraIglesias.com': omitidas_ei += 1; continue
        if es_catolica(nombre) or 'catol' in r['denomination'].lower(): omitidas_cat += 1; continue
        fte = 'EncuentraIglesias.com (directorio de terceros)' if r['source'] == 'EncuentraIglesias.com' else r['source']
        if (nombre, fte) in ya: continue
        loc, reg = ubicar(r, cfg)
        loc = loc or 'Sin localidad'; reg = reg or f"Sin {cfg['region_nombre']}"
        if r['city'].strip(): loc = r['city'].strip(); reg = r['state_province'].strip() or reg
        direccion = r['address'].strip() or (r['notes'].replace('Region:', '').strip() if r['notes'].startswith('Region:') else '')
        base = slugify(f"{nombre} {loc if loc != 'Sin localidad' else ''}") or slugify(r['id'])
        slug, n = base, 1
        while slug in vistos: n += 1; slug = f'{base}-{n}'
        vistos.add(slug)
        fuente = 'EncuentraIglesias.com (directorio de terceros)' if r['source'] == 'EncuentraIglesias.com' else r['source']
        out.append({
            'slug': slug, 'nombre': nombre, 'entidad': (r['association'] or nombre).strip(), 'entidad_slug': slugify(r['association'] or nombre), 'filial': None,
            'direccion': direccion, 'localidad': loc, 'localidad_slug': slugify(loc) or 'sin-localidad', 'provincia': reg, 'provincia_slug': slugify(reg) or 'sin-region',
            'pais': pais, 'pais_slug': iso, 'registro_ci': r['registration_number'].strip() or None, 'fuente': fuente,
            'denominacion': DENOM.get(r['denomination'].strip(), r['denomination'].strip() or None), 'religion': 'Cristiana',
            'web': r['website'].strip() or None, 'facebook': None, 'instagram': None, 'google_maps': None,
            'telefono': r['phone'].strip() or None, 'email': r['email'].strip() or None, 'horarios': None,
            'lat': float(r['latitude']) if r['latitude'].strip() else None, 'lon': float(r['longitude']) if r['longitude'].strip() else None,
            'reclamada': False, 'fuente_url': r['source_url'].strip() or None,
        })
    todo = existentes + out
    nregiones = guardar(dst, todo)
    ubic = sum(1 for i in out if i['localidad'] != 'Sin localidad')
    print(f'{pais}: {len(out)} fichas nuevas ({ubic} con localidad = {100*ubic//max(len(out),1)}%) -> {dst}/iglesias/ ({nregiones} archivos, {len(todo)} en total)')
    print(f'  omitidas por marcas católicas: {omitidas_cat}' + (f' | omitidas de EncuentraIglesias: {omitidas_ei}' if sin_ei else ''))
    print('  regiones:', collections.Counter(i['provincia'] for i in out).most_common(8))
    return {'nuevas': len(out), 'con_localidad': ubic, 'catolicas': omitidas_cat}

if __name__ == '__main__':
    a = [x for x in sys.argv[1:] if not x.startswith('--')]
    main(a[0], a[1], a[2], anexar='--anexar' in sys.argv, sin_ei='--sin-encuentraiglesias' in sys.argv)
