#!/usr/bin/env python3
"""Colombia: carga inicial desde data/co/raw/churches_colombia.csv (recopilación manual de varias fuentes).

Normaliza a data/co/iglesias/<departamento>.json. La mayoría de las filas viene de EncuentraIglesias.com y no trae
ciudad ni departamento: la localidad se deduce del slug de la URL de origen y el departamento se infiere de la ciudad
cuando es una ciudad conocida. Lo que no se puede ubicar queda en "Sin departamento" / "Sin localidad".

Uso: python3 -I scripts/co/csv_inicial.py data/co/raw/churches_colombia.csv data/co
"""
import csv, re, sys, os, unicodedata
sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', 'comunes'))
from datos import guardar

def slugify(s):
    s = unicodedata.normalize('NFKD', s or '').encode('ascii', 'ignore').decode()
    return re.sub(r'[^a-zA-Z0-9]+', '-', s).strip('-').lower()

def titulo(s):
    small = {'de', 'del', 'la', 'las', 'los', 'el', 'y', 'en', 'a', 'al', 'dc'}
    out = []
    for i, w in enumerate(re.sub(r'\s+', ' ', s).strip().lower().split(' ')):
        out.append(w.upper() if w == 'dc' else (w if (w in small and i > 0) else w.capitalize()))
    return ' '.join(out).replace('Dc', 'D.C.').replace('DC', 'D.C.')

# ciudad (slug) -> (ciudad, departamento)
CIUDADES = {
 'bogota': ('Bogotá D.C.', 'Bogotá D.C.'), 'bogota-dc': ('Bogotá D.C.', 'Bogotá D.C.'), 'bogota-d-c': ('Bogotá D.C.', 'Bogotá D.C.'),
 'medellin': ('Medellín', 'Antioquia'), 'bello': ('Bello', 'Antioquia'), 'itagui': ('Itagüí', 'Antioquia'), 'envigado': ('Envigado', 'Antioquia'), 'sabaneta': ('Sabaneta', 'Antioquia'),
 'copacabana': ('Copacabana', 'Antioquia'), 'caldas': ('Caldas', 'Antioquia'), 'el-retiro': ('El Retiro', 'Antioquia'), 'rionegro': ('Rionegro', 'Antioquia'), 'la-estrella': ('La Estrella', 'Antioquia'), 'apartado': ('Apartadó', 'Antioquia'), 'turbo': ('Turbo', 'Antioquia'),
 'cali': ('Cali', 'Valle del Cauca'), 'palmira': ('Palmira', 'Valle del Cauca'), 'buenaventura': ('Buenaventura', 'Valle del Cauca'), 'tulua': ('Tuluá', 'Valle del Cauca'), 'buga': ('Buga', 'Valle del Cauca'), 'cartago': ('Cartago', 'Valle del Cauca'), 'jamundi': ('Jamundí', 'Valle del Cauca'), 'yumbo': ('Yumbo', 'Valle del Cauca'),
 'barranquilla': ('Barranquilla', 'Atlántico'), 'soledad': ('Soledad', 'Atlántico'), 'malambo': ('Malambo', 'Atlántico'),
 'cartagena': ('Cartagena', 'Bolívar'), 'cartagena-de-indias': ('Cartagena', 'Bolívar'), 'magangue': ('Magangué', 'Bolívar'),
 'bucaramanga': ('Bucaramanga', 'Santander'), 'floridablanca': ('Floridablanca', 'Santander'), 'giron': ('Girón', 'Santander'), 'piedecuesta': ('Piedecuesta', 'Santander'), 'barrancabermeja': ('Barrancabermeja', 'Santander'),
 'cucuta': ('Cúcuta', 'Norte de Santander'), 'ocana': ('Ocaña', 'Norte de Santander'), 'pamplona': ('Pamplona', 'Norte de Santander'),
 'pereira': ('Pereira', 'Risaralda'), 'dosquebradas': ('Dosquebradas', 'Risaralda'), 'manizales': ('Manizales', 'Caldas'), 'armenia': ('Armenia', 'Quindío'),
 'ibague': ('Ibagué', 'Tolima'), 'espinal': ('Espinal', 'Tolima'), 'santa-marta': ('Santa Marta', 'Magdalena'), 'cienaga': ('Ciénaga', 'Magdalena'),
 'villavicencio': ('Villavicencio', 'Meta'), 'acacias': ('Acacías', 'Meta'), 'pasto': ('Pasto', 'Nariño'), 'ipiales': ('Ipiales', 'Nariño'), 'tumaco': ('Tumaco', 'Nariño'),
 'neiva': ('Neiva', 'Huila'), 'pitalito': ('Pitalito', 'Huila'), 'monteria': ('Montería', 'Córdoba'), 'popayan': ('Popayán', 'Cauca'), 'valledupar': ('Valledupar', 'Cesar'),
 'sincelejo': ('Sincelejo', 'Sucre'), 'tunja': ('Tunja', 'Boyacá'), 'duitama': ('Duitama', 'Boyacá'), 'sogamoso': ('Sogamoso', 'Boyacá'),
 'soacha': ('Soacha', 'Cundinamarca'), 'chia': ('Chía', 'Cundinamarca'), 'zipaquira': ('Zipaquirá', 'Cundinamarca'), 'facatativa': ('Facatativá', 'Cundinamarca'), 'fusagasuga': ('Fusagasugá', 'Cundinamarca'), 'girardot': ('Girardot', 'Cundinamarca'), 'mosquera': ('Mosquera', 'Cundinamarca'), 'madrid': ('Madrid', 'Cundinamarca'), 'cajica': ('Cajicá', 'Cundinamarca'),
 'riohacha': ('Riohacha', 'La Guajira'), 'maicao': ('Maicao', 'La Guajira'), 'quibdo': ('Quibdó', 'Chocó'), 'florencia': ('Florencia', 'Caquetá'), 'yopal': ('Yopal', 'Casanare'), 'arauca': ('Arauca', 'Arauca'), 'leticia': ('Leticia', 'Amazonas'), 'san-andres': ('San Andrés', 'San Andrés y Providencia'), 'mocoa': ('Mocoa', 'Putumayo'), 'san-jose-del-guaviare': ('San José del Guaviare', 'Guaviare'), 'puerto-carreno': ('Puerto Carreño', 'Vichada'), 'inirida': ('Inírida', 'Guainía'), 'mitu': ('Mitú', 'Vaupés'),
}
# Localidades de Bogotá que aparecen en los slugs
LOCALIDADES_BOGOTA = {'suba','usaquen','chapinero','kennedy','engativa','fontibon','bosa','ciudad-bolivar','usme','teusaquillo','puente-aranda','rafael-uribe-uribe','san-cristobal','tunjuelito','antonio-narino','barrios-unidos','los-martires','santa-fe','la-candelaria','localidad-suroccidente','localidad-suba'}
DENOM = {'Cristiana': 'Evangélica', 'Evangélica': 'Evangélica', 'Pentecostal': 'Pentecostal', 'Bautista': 'Bautista', 'Adventista del Séptimo Día': 'Adventista del Séptimo Día', 'Anglicana': 'Anglicana', 'Presbiteriana': 'Presbiteriana / Reformada', 'Luterana': 'Luterana', 'Múltiples': None}

ARREGLOS_CIUDAD = {'medellin-proximamente-comuna-12': 'medellin', 'laureles': 'medellin', 'san-cristobal': 'medellin', 'sector-chipre': 'manizales', 'quindio': 'armenia', 'bogota': 'bogota-dc'}
EXTRA = {'san-jose-de-cucuta': 'cucuta', 'cucuta-ns': 'cucuta', 'comuna-5-castilla': 'medellin', 'comuna-11-laureles-estadio': 'medellin', 'barrios-unidos': 'bogota-dc', 'localidad-suroccidente': 'bogota-dc',
         'chiquinquira': ('Chiquinquirá', 'Boyacá'), 'tierralta': ('Tierralta', 'Córdoba'), 'amalfi': ('Amalfi', 'Antioquia')}
SIN_INFO = {'iglesia', 'templo', 'capilla', 'oratorio', 'ministerio', 'centro'}
def ubicar(r):
    """Devuelve (localidad, departamento) a partir de city/state o del slug de la URL."""
    if r['city'].strip():
        c = r['city'].strip(); d = r['state_province'].strip()
        k = ARREGLOS_CIUDAD.get(slugify(c), slugify(c))
        if k in CIUDADES: return CIUDADES[k]
        if 'antioquia' in slugify(c) or 'antioquia' in slugify(d): return ('Sin localidad', 'Antioquia')
        if slugify(d) in CIUDADES: return (c, CIUDADES[slugify(d)][1])
        return (c, d or 'Sin departamento')
    m = re.search(r'/iglesia/(.+?)(?:-colombia)?(?:-\d+)?$', r['source_url'])
    if not m: return ('Sin localidad', 'Sin departamento')
    resto = m.group(1)
    nombre_slug = slugify(r['name'])
    if resto.startswith(nombre_slug): resto = resto[len(nombre_slug):].strip('-')
    if not resto or resto in SIN_INFO: return ('Sin localidad', 'Sin departamento')
    if resto in EXTRA: v = EXTRA[resto]; return CIUDADES[v] if isinstance(v, str) else v
    if resto in CIUDADES: return CIUDADES[resto]
    for k in sorted(CIUDADES, key=len, reverse=True):
        if resto.endswith('-' + k) or resto == k:
            barrio = resto[: -len(k)].strip('-')
            loc, dep = CIUDADES[k]
            return (loc, dep)
    if resto in LOCALIDADES_BOGOTA or any(resto.endswith(b) for b in LOCALIDADES_BOGOTA): return ('Bogotá D.C.', 'Bogotá D.C.')
    return (titulo(resto.replace('-', ' ')), 'Sin departamento')

def main(src, dst):
    rows = list(csv.DictReader(open(src, encoding='utf-8')))
    out, vistos = [], set()
    for r in rows:
        if r['name'].lower().startswith('directorio ') and 'encuentraiglesias' in r['name'].lower(): continue  # fila meta
        loc, dep = ubicar(r)
        direccion = r['address'].strip() or (r['notes'].replace('Region:', '').strip() if r['notes'].startswith('Region:') else '')
        base = slugify(f"{r['name']} {loc if loc != 'Sin localidad' else ''}") or slugify(r['id'])
        slug, n = base, 1
        while slug in vistos: n += 1; slug = f'{base}-{n}'
        vistos.add(slug)
        fuente = {'EncuentraIglesias.com': 'EncuentraIglesias.com (directorio de terceros)', 'Redil.org (FIBEC)': 'Redil.org (FIBEC)', 'FIBEC - El Redil (redil.org)': 'Redil.org (FIBEC)',
                  'Directorio Iglesias Bautistas Colombia': 'Directorio Iglesias Bautistas Colombia', 'Ministerio del Interior Colombia': 'Ministerio del Interior de Colombia'}.get(r['source'], r['source'])
        out.append({
            'slug': slug, 'nombre': re.sub(r'\s+', ' ', r['name']).strip(), 'entidad': (r['association'] or r['name']).strip(), 'entidad_slug': slugify(r['association'] or r['name']), 'filial': None,
            'direccion': direccion, 'localidad': loc, 'localidad_slug': slugify(loc) or 'sin-localidad', 'provincia': dep, 'provincia_slug': slugify(dep) or 'sin-departamento',
            'pais': 'Colombia', 'pais_slug': 'co', 'registro_ci': r['registration_number'].strip() or None, 'fuente': fuente,
            'denominacion': DENOM.get(r['denomination'].strip(), r['denomination'].strip() or None), 'religion': 'Cristiana',
            'web': r['website'].strip() or None, 'facebook': None, 'instagram': None, 'google_maps': None,
            'telefono': r['phone'].strip() or None, 'email': r['email'].strip() or None, 'horarios': None,
            'lat': float(r['latitude']) if r['latitude'].strip() else None, 'lon': float(r['longitude']) if r['longitude'].strip() else None,
            'reclamada': False, 'fuente_url': r['source_url'].strip() or None,
        })
    n = guardar(dst, out)
    import collections
    print(f'{len(out)} fichas -> {dst}/iglesias/ ({n} archivos)')
    print('departamentos:', collections.Counter(i['provincia'] for i in out).most_common(12))
    print('localidades sin dato:', sum(1 for i in out if i['localidad'] == 'Sin localidad'))

if __name__ == '__main__': main(sys.argv[1], sys.argv[2])
