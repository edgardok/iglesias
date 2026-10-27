#!/usr/bin/env python3
"""Separa las fichas de un país entre las que tienen nombre en español (se publican) y el resto (se archivan).

El archivo queda en data/_archivo/<iso>/iglesias/<region>.json, con la misma estructura que data/<iso>/, para poder
volver a publicarlo cuando cambie el alcance. No se borra nada: lo archivado sigue en git.

Criterio sobre el nombre de la ficha:
  - contiene una palabra característica del español (iglesia, ministerio, templo, de la, etc.), o
  - contiene un carácter propio del español (ñ, vocales con tilde) sin ser vietnamita, o
  - empieza con un artículo (El, La, Los, Las) y no trae palabras de iglesias en inglés.
Los nombres bilingües ("Iglesia Bautista Church") cuentan como español. Es una heurística: una iglesia de habla hispana
con nombre en inglés queda archivada hasta que la reclame.

Uso: python3 -I scripts/comunes/idioma.py data/us
"""
import os, re, sys
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from datos import cargar, guardar

PALABRAS = (r"iglesia|iglesias|ministerio|ministerios|templo|cristiana|cristiano|cristianos|evang[eé]lica|evang[eé]lico|hispana|hispano|hispanos|"
            r"latina|latino|latinoamericana|comunidad|asamblea|asambleas|misi[oó]n|misionera|misionero|santuario|capilla|casa de|centro cristiano|"
            r"centro evang[eé]lico|nueva vida|vida nueva|de dios|del se[nñ]or|palabra de|esperanza|resurrecci[oó]n|avivamiento|alabanza|adoraci[oó]n|"
            r"la verdad|buen pastor|rey de reyes|jehov[aá]|jesucristo|de la")
RE = re.compile(r"(?<![a-zA-Z])(" + PALABRAS + r")(?![a-zA-Z])", re.I)
CARACTER_ES = re.compile(r"[ñáéíóúü¿¡]", re.I)
VIETNAMITA = re.compile("[Ạ-ỹđĐơƠưƯăĂ]")
ARTICULO = re.compile(r"^(el|la|los|las)\s+", re.I)
INGLES = re.compile(r"\b(church|baptist|methodist|presbyterian|lutheran|episcopal|chapel|temple|congregation|assembly of god|fellowship|ministries|christian|catholic|united|first|mount|saint|st)\b", re.I)

def es_espanol(i):
    n = i['nombre']
    if RE.search(n): return True
    if CARACTER_ES.search(n) and not VIETNAMITA.search(n): return True
    return bool(ARTICULO.search(n)) and not INGLES.search(n)

def main(carpeta):
    iso = os.path.basename(carpeta.rstrip('/'))
    ig = cargar(carpeta)
    es = [i for i in ig if es_espanol(i)]
    resto = [i for i in ig if not es_espanol(i)]
    destino = os.path.join(os.path.dirname(carpeta.rstrip('/')), '_archivo', iso)
    archivado = cargar(destino) if os.path.isdir(os.path.join(destino, 'iglesias')) else []
    ya = {i['slug'] for i in archivado}
    guardar(destino, archivado + [i for i in resto if i['slug'] not in ya])
    guardar(carpeta, es)
    print(f'{iso}: {len(ig)} fichas -> {len(es)} en español (publicadas), {len(resto)} archivadas en {destino}/iglesias/')
    return es, resto

if __name__ == '__main__':
    main(sys.argv[1])
