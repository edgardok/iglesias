"""Listas de regiones de primer nivel por país, para ubicar fichas a partir del final de la URL de origen.

Cada país: nombre, tipo de región, tokens que indican el país al final del slug, y un diccionario
{(tokens del slug,): 'Nombre canónico'}. Gana la coincidencia más larga al final del slug.
Las ciudades salen del mismo slug (sin tildes, porque el slug no las tiene).
"""

def _d(*pares):
    out = {}
    for nombre, *slugs in pares:
        for s in slugs: out[tuple(s.split('-'))] = nombre
    return out

US_ESTADOS = [('Alabama','al'),('Alaska','ak'),('Arizona','az'),('Arkansas','ar'),('California','ca'),('Colorado','co'),('Connecticut','ct'),('Delaware','de'),('Florida','fl'),('Georgia','ga'),('Hawái','hawaii','hi'),('Idaho','id'),('Illinois','il'),('Indiana','in'),('Iowa','ia'),('Kansas','ks'),('Kentucky','ky'),('Luisiana','louisiana','la'),('Maine','me'),('Maryland','md'),('Massachusetts','ma'),('Míchigan','michigan','mi'),('Minnesota','mn'),('Misisipi','mississippi','ms'),('Misuri','missouri','mo'),('Montana','mt'),('Nebraska','ne'),('Nevada','nv'),('Nueva Hampshire','new-hampshire','nh'),('Nueva Jersey','new-jersey','nj'),('Nuevo México','new-mexico','nm'),('Nueva York','new-york','ny'),('Carolina del Norte','north-carolina','nc'),('Dakota del Norte','north-dakota','nd'),('Ohio','oh'),('Oklahoma','ok'),('Oregón','oregon','or'),('Pensilvania','pennsylvania','pa'),('Rhode Island','rhode-island','ri'),('Carolina del Sur','south-carolina','sc'),('Dakota del Sur','south-dakota','sd'),('Tennessee','tn'),('Texas','tx'),('Utah','ut'),('Vermont','vt'),('Virginia','va'),('Washington','wa'),('Virginia Occidental','west-virginia','wv'),('Wisconsin','wi'),('Wyoming','wy'),('Distrito de Columbia','district-of-columbia','dc')]

def _us():
    full, abbr = {}, {}
    for nombre, *toks in US_ESTADOS:
        for t in toks:
            if len(t) == 2 and '-' not in t: abbr[t] = nombre
            if len(t) > 2 or t not in abbr: pass
        for t in toks:
            if len(t) > 2: full[tuple(t.split('-'))] = nombre
        full[tuple(nombre.lower().split())] = nombre if False else full.get(tuple(nombre.lower().split()), nombre)
    # nombres de un solo token que coinciden con su nombre en inglés
    for nombre, *toks in US_ESTADOS:
        for t in toks:
            if len(t) > 2: full[tuple(t.split('-'))] = nombre
        full[tuple(nombre.lower().replace('á','a').replace('í','i').replace('ó','o').split())] = nombre
    for k in [('alabama',), ('alaska',), ('arizona',), ('arkansas',), ('california',), ('colorado',), ('connecticut',), ('delaware',), ('florida',), ('georgia',), ('idaho',), ('illinois',), ('indiana',), ('iowa',), ('kansas',), ('kentucky',), ('maine',), ('maryland',), ('massachusetts',), ('minnesota',), ('montana',), ('nebraska',), ('nevada',), ('ohio',), ('oklahoma',), ('tennessee',), ('texas',), ('utah',), ('vermont',), ('virginia',), ('washington',), ('wisconsin',), ('wyoming',)]:
        full[k] = k[0].title()
    return full, abbr
_US_FULL, _US_ABBR = _us()
# "carolina", "dakota", "york", "jersey", "hampshire" solos no se asumen: son ambiguos (norte/sur)

REGIONES = {
 'mx': {'pais': 'México', 'region_nombre': 'estado', 'marcas': [('mexico',)], 'abrev': {}, 'region_como_localidad': True,
   'regiones': _d(('Aguascalientes','aguascalientes'),('Baja California','baja-california','bc','baja-california-norte'),('Baja California Sur','baja-california-sur','bcs'),('Campeche','campeche'),('Chiapas','chiapas'),('Chihuahua','chihuahua'),
     ('Ciudad de México','ciudad-de-mexico','cdmx','distrito-federal'),('Coahuila','coahuila','coahuila-de-zaragoza'),('Colima','colima'),('Durango','durango'),('Guanajuato','guanajuato'),('Guerrero','guerrero'),('Hidalgo','hidalgo'),('Jalisco','jalisco'),
     ('Estado de México','estado-de-mexico','edomex'),('Michoacán','michoacan','michoacan-de-ocampo'),('Morelos','morelos'),('Nayarit','nayarit'),('Nuevo León','nuevo-leon','nl'),('Oaxaca','oaxaca'),('Puebla','puebla'),('Querétaro','queretaro','qro'),('Quintana Roo','quintana-roo','q-roo'),
     ('San Luis Potosí','san-luis-potosi','slp'),('Sinaloa','sinaloa'),('Sonora','sonora'),('Tabasco','tabasco'),('Tamaulipas','tamaulipas'),('Tlaxcala','tlaxcala'),('Veracruz','veracruz','veracruz-de-ignacio-de-la-llave'),('Yucatán','yucatan'),('Zacatecas','zacatecas'))},
 'es': {'pais': 'España', 'region_nombre': 'comunidad', 'marcas': [('espana',)], 'abrev': {}, 'region_como_localidad': False,
   'regiones': _d(('Andalucía','andalusia','andalucia','sevilla','malaga','granada','cordoba','cadiz','almeria','huelva','jaen'),('Cataluña','catalonia','catalunya','cataluna','barcelona','girona','gerona','tarragona','lleida','lerida'),('Aragón','aragon','huesca','zaragoza','teruel'),
     ('Castilla y León','castile-and-leon','castilla-y-leon','castile-leon','leon','salamanca','valladolid','avila','segovia','soria','burgos','zamora','palencia'),('Castilla-La Mancha','castile-la-mancha','castilla-la-mancha','toledo','ciudad-real','albacete','cuenca','guadalajara'),
     ('Comunidad de Madrid','madrid','community-of-madrid','comunidad-de-madrid'),('Comunitat Valenciana','valencian-community','comunidad-valenciana','comunitat-valenciana','valenciana','valencia','alicante','alacant','castellon'),
     ('Extremadura','extremadura','caceres','badajoz'),('Galicia','galicia','a-coruna','la-coruna','lugo','ourense','orense','pontevedra'),('País Vasco','basque-country','pais-vasco','gipuzkoa','guipuzcoa','bizkaia','vizcaya','alava','araba'),('Navarra','navarre','navarra'),
     ('La Rioja','la-rioja','rioja'),('Cantabria','cantabria'),('Asturias','asturias','principado-de-asturias'),('Islas Baleares','balearic-islands','illes-balears','baleares','mallorca'),('Canarias','canary-islands','canarias','tenerife','las-palmas','santa-cruz-de-tenerife'),
     ('Región de Murcia','murcia','region-de-murcia'),('Ceuta','ceuta'),('Melilla','melilla'))},
 'us': {'pais': 'Estados Unidos', 'region_nombre': 'estado', 'marcas': [('estados', 'unidos')], 'abrev': _US_ABBR, 'region_como_localidad': False, 'regiones': _US_FULL},
 'cl': {'pais': 'Chile', 'region_nombre': 'región', 'marcas': [('chile',)], 'abrev': {}, 'region_como_localidad': True,
   'regiones': _d(('Arica y Parinacota','arica-y-parinacota','arica'),('Tarapacá','tarapaca','iquique'),('Antofagasta','antofagasta'),('Atacama','atacama','copiapo'),('Coquimbo','coquimbo','la-serena'),('Valparaíso','valparaiso','region-de-valparaiso'),('Metropolitana de Santiago','region-metropolitana','metropolitana','santiago'),
     ("O'Higgins",'ohiggins','o-higgins','rancagua'),('Maule','maule','talca'),('Ñuble','nuble','chillan'),('Biobío','biobio','bio-bio','concepcion'),('La Araucanía','la-araucania','araucania','temuco'),('Los Ríos','los-rios','region-de-los-rios','valdivia'),('Los Lagos','los-lagos','region-de-los-lagos','osorno','puerto-montt'),
     ('Aysén','aysen','coyhaique'),('Magallanes','magallanes','punta-arenas'))},
 'pe': {'pais': 'Perú', 'region_nombre': 'departamento', 'marcas': [('per',), ('peru',)], 'abrev': {}, 'region_como_localidad': True,
   'regiones': _d(('Amazonas','amazonas'),('Áncash','ancash'),('Apurímac','apurimac'),('Arequipa','arequipa'),('Ayacucho','ayacucho'),('Cajamarca','cajamarca'),('Callao','callao'),('Cusco','cusco','cuzco'),('Huancavelica','huancavelica'),('Huánuco','huanuco'),('Ica','ica'),('Junín','junin'),
     ('La Libertad','la-libertad','libertad'),('Lambayeque','lambayeque'),('Lima','lima'),('Loreto','loreto'),('Madre de Dios','madre-de-dios'),('Moquegua','moquegua'),('Pasco','pasco'),('Piura','piura'),('Puno','puno'),('San Martín','san-martin'),('Tacna','tacna'),('Tumbes','tumbes'),('Ucayali','ucayali'))},
 'ar': {'pais': 'Argentina', 'region_nombre': 'provincia', 'marcas': [('argentina',)], 'abrev': {}, 'region_como_localidad': False,
   'regiones': _d(('Buenos Aires','buenos-aires'),('Catamarca','catamarca'),('Chaco','chaco'),('Chubut','chubut'),('Ciudad Autónoma de Buenos Aires','capital-federal','ciudad-autonoma-de-buenos-aires','caba'),('Córdoba','cordoba'),('Corrientes','corrientes'),('Entre Ríos','entre-rios'),('Formosa','formosa'),('Jujuy','jujuy'),('La Pampa','la-pampa'),('La Rioja','la-rioja'),
     ('Mendoza','mendoza'),('Misiones','misiones'),('Neuquén','neuquen'),('Río Negro','rio-negro'),('Salta','salta'),('San Juan','san-juan'),('San Luis','san-luis'),('Santa Cruz','santa-cruz'),('Santa Fe','santa-fe'),('Santiago del Estero','santiago-del-estero'),('Tierra del Fuego','tierra-del-fuego'),('Tucumán','tucuman'))},
 'br': {'pais': 'Brasil', 'region_nombre': 'estado', 'marcas': [('brasil',)], 'abrev': {}, 'region_como_localidad': True,
   'regiones': _d(('Acre','acre'),('Alagoas','alagoas'),('Amapá','amapa'),('Amazonas','amazonas'),('Bahía','bahia'),('Ceará','ceara'),('Distrito Federal','distrito-federal','brasilia'),('Espírito Santo','espirito-santo'),('Goiás','goias'),('Maranhão','maranhao'),('Mato Grosso','mato-grosso'),('Mato Grosso do Sul','mato-grosso-do-sul'),
     ('Minas Gerais','minas-gerais'),('Pará','para'),('Paraíba','paraiba'),('Paraná','parana'),('Pernambuco','pernambuco'),('Piauí','piaui'),('Río de Janeiro','rio-de-janeiro'),('Río Grande do Norte','rio-grande-do-norte'),('Río Grande do Sul','rio-grande-do-sul'),('Rondônia','rondonia'),('Roraima','roraima'),
     ('Santa Catarina','santa-catarina'),('São Paulo','sao-paulo'),('Sergipe','sergipe'),('Tocantins','tocantins'))},
}

# Marcas de contenido católico inequívoco en el nombre (el directorio no incluye iglesias católicas)
CATOLICAS = ('parroquia', 'catedral', 'basilica', 'arquidiocesis', 'arzobispado', 'diocesis', 'obispado', 'santuario', 'nuestra senora', 'virgen de', 'virgen del', 'virgen maria', 'gruta de la virgen', 'our lady', 'catholic', 'catolic', 'paroquia', 'catedral', 'sagrado corazon', 'sacred heart', 'immaculate', 'inmaculada', 'monasterio', 'convento', 'abadia', 'seminario')
