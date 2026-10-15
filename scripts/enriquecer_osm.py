#!/usr/bin/env python3
"""Fusiona los templos de OpenStreetMap con data/iglesias.json.

- Asigna provincia y localidad a cada punto OSM con la API georef (apis.datos.gob.ar), por lote.
- Si un punto OSM coincide con una ficha del registro (mismo nombre normalizado y misma localidad o
  misma provincia con nombre muy específico), le pega coordenadas, web, redes, teléfono y horarios.
- Si no coincide, lo agrega como ficha nueva con fuente OpenStreetMap.

Uso: python3 -I scripts/enriquecer_osm.py data/raw/osm-place-of-worship.json data/iglesias.json
"""
import json, re, sys, unicodedata, urllib.request, time, collections

def slugify(s):
    s = unicodedata.normalize('NFKD', s or '').encode('ascii', 'ignore').decode()
    return re.sub(r'[^a-zA-Z0-9]+', '-', s).strip('-').lower()

RUIDO = {'iglesia','parroquia','templo','capilla','evangelica','cristiana','de','del','la','las','los','el','y','en','san','santa','santo','nuestra','senora','ntra','sra','salon','reino','congregacion','ministerio','centro','comunidad','asociacion'}
def clave(nombre):
    toks = [t for t in slugify(nombre).split('-') if t and t not in RUIDO and not t.isdigit()]
    return ' '.join(sorted(toks))

DENOM = {'catholic':'Católica','roman_catholic':'Católica','evangelical':'Evangélica','pentecostal':'Pentecostal','mormon':'Iglesia de Jesucristo de los Santos de los Últimos Días','jehovahs_witness':'Testigos de Jehová','baptist':'Bautista','lutheran':'Luterana','seventh_day_adventist':'Adventista del Séptimo Día','protestant':'Protestante','methodist':'Metodista','anglican':'Anglicana','orthodox':'Ortodoxa','presbyterian':'Presbiteriana','new_apostolic':'Nueva Apostólica','salvation_army':'Ejército de Salvación','mennonite':'Menonita','reformed':'Reformada','assemblies_of_god':'Asambleas de Dios','lubavitch':'Jabad Lubavitch','orthodox_jewish':'Judía ortodoxa','conservative':'Judía conservadora','sunni':'Musulmana sunita','shia':'Musulmana chiita'}
RELIG = {'christian':'Cristiana','jewish':'Judía','muslim':'Musulmana','buddhist':'Budista','hindu':'Hinduista','bahai':"Bahá'í",'spiritualist':'Espiritista','popular':'Religiosidad popular'}

def georef(puntos):
    """puntos: lista de (lat, lon). Devuelve lista de dicts georef 'ubicacion'."""
    out = []
    for i in range(0, len(puntos), 500):
        lote = [{'lat': la, 'lon': lo, 'campos': 'completo'} for la, lo in puntos[i:i+500]]
        for intento in range(4):
            try:
                req = urllib.request.Request('https://apis.datos.gob.ar/georef/api/ubicacion', data=json.dumps({'ubicaciones': lote}).encode(),
                                             headers={'Content-Type': 'application/json', 'User-Agent': 'iglesias-ar-mvp/0.1'})
                res = json.load(urllib.request.urlopen(req, timeout=120))
                out += [r.get('ubicacion', {}) for r in res['resultados']]
                break
            except Exception as e:
                print('georef reintento', intento, e, file=sys.stderr); time.sleep(5 * (intento + 1))
        else:
            out += [{} for _ in lote]
        print(f'georef {min(i+500, len(puntos))}/{len(puntos)}', file=sys.stderr)
    return out

def main(src_osm, dst):
    iglesias = json.load(open(dst, encoding='utf-8'))
    els = [e for e in json.load(open(src_osm))['elements'] if e.get('tags', {}).get('name')]
    pts = [((e.get('lat') or e['center']['lat']), (e.get('lon') or e['center']['lon'])) for e in els]
    ubic = georef(pts)

    idx = collections.defaultdict(list)
    for ig in iglesias:
        idx[(clave(ig['nombre']), ig['localidad_slug'])].append(ig)
        idx[(clave(ig['entidad']), ig['localidad_slug'])].append(ig)
    slugs = {ig['slug'] for ig in iglesias}

    nuevos, pegados = 0, 0
    for e, (lat, lon), u in zip(els, pts, ubic):
        t = e['tags']
        prov = (u.get('provincia') or {}).get('nombre') or t.get('addr:state') or 'Sin provincia'
        loc = t.get('addr:city') or (u.get('municipio') or {}).get('nombre') or (u.get('departamento') or {}).get('nombre') or 'Sin localidad'
        if slugify(prov) == 'ciudad-autonoma-de-buenos-aires': loc = 'Ciudad de Buenos Aires'
        prov_slug = 'caba' if slugify(prov) == 'ciudad-autonoma-de-buenos-aires' else (slugify(prov) or 'sin-provincia')
        web = t.get('website') or t.get('contact:website')
        fb = t.get('contact:facebook') or t.get('facebook')
        if fb and not fb.startswith('http'): fb = 'https://www.facebook.com/' + fb.lstrip('@')
        ig_ = t.get('contact:instagram') or t.get('instagram')
        if ig_ and not ig_.startswith('http'): ig_ = 'https://www.instagram.com/' + ig_.lstrip('@')
        tel = t.get('phone') or t.get('contact:phone')
        mail = t.get('email') or t.get('contact:email')
        horarios = t.get('service_times') or t.get('opening_hours')
        direccion = ' '.join(filter(None, [t.get('addr:street'), t.get('addr:housenumber')])).strip()
        denom = DENOM.get(t.get('denomination')) or (t.get('denomination') or '').replace('_', ' ').capitalize() or None
        relig = RELIG.get(t.get('religion'))
        osm_id = f"{e['type']}/{e['id']}"
        extra = {'web': web, 'facebook': fb, 'instagram': ig_, 'telefono': tel, 'email': mail, 'horarios': horarios, 'lat': lat, 'lon': lon, 'denominacion': denom, 'religion': relig, 'osm_id': osm_id}

        cand = idx.get((clave(t['name']), slugify(loc)), [])
        cand = [c for c in cand if c['provincia_slug'] == prov_slug and not c.get('osm_id')] if cand else []
        if len(cand) == 1 and clave(t['name']):
            for k, v in extra.items():
                if v and not cand[0].get(k): cand[0][k] = v
            if not cand[0]['direccion'] and direccion: cand[0]['direccion'] = direccion
            pegados += 1
            continue

        base = slugify(f"{t['name']} {loc}") or f'osm-{e["id"]}'
        slug, n = base, 1
        while slug in slugs: n += 1; slug = f'{base}-{n}'
        slugs.add(slug)
        iglesias.append({
            'slug': slug, 'nombre': t['name'].strip(), 'entidad': t['name'].strip(), 'entidad_slug': slugify(t['name']), 'filial': None,
            'direccion': direccion, 'localidad': loc, 'localidad_slug': slugify(loc) or 'sin-localidad', 'provincia': prov, 'provincia_slug': prov_slug,
            'registro_ci': None, 'fuente': 'OpenStreetMap (ODbL)', 'google_maps': None, 'reclamada': False, **extra,
        })
        nuevos += 1

    json.dump(iglesias, open(dst, 'w', encoding='utf-8'), ensure_ascii=False, indent=0)
    print(f'OSM: {len(els)} con nombre, {pegados} pegados a fichas del registro, {nuevos} fichas nuevas. Total {len(iglesias)}')

if __name__ == '__main__':
    main(sys.argv[1], sys.argv[2])
