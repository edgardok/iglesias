#!/bin/sh
# Una consulta por provincia (ISO 3166-2). Salida: data/raw/osm-prov/<ISO>.json con ids de templos dentro de la provincia.
mkdir -p data/raw/osm-prov
for iso in A B C D E F G H J K L M N P Q R S T U V W X Y Z; do
  out="data/raw/osm-prov/AR-$iso.json"
  [ -s "$out" ] && grep -q '"elements"' "$out" && continue
  Q="[out:json][timeout:300];area[\"ISO3166-2\"=\"AR-$iso\"]->.p;nwr[\"amenity\"=\"place_of_worship\"](area.p);out ids;"
  curl -sL --max-time 400 -A "iglesias-ar-mvp/0.1" --data-urlencode "data=$Q" https://overpass-api.de/api/interpreter -o "$out"
  echo "AR-$iso $(wc -c < "$out") bytes"
  sleep 3
done
