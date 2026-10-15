[out:json][timeout:600];
area["ISO3166-1"="AR"][admin_level=2]->.ar;
(
  nwr["amenity"="place_of_worship"](area.ar);
);
out center tags;
