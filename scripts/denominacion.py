#!/usr/bin/env python3
"""Infiere denominación y religión a partir del nombre de la entidad, para las fichas que no la tienen."""
import json, re, sys, unicodedata
def norm(s): return unicodedata.normalize('NFKD', s).encode('ascii','ignore').decode().lower()
REGLAS = [  # (patrón, denominación, religión)
    (r'testigos de jehova', 'Testigos de Jehová', 'Cristiana'),
    (r'santos de los ultimos dias|mormon', 'Iglesia de Jesucristo de los Santos de los Últimos Días', 'Cristiana'),
    (r'adventist', 'Adventista del Séptimo Día', 'Cristiana'),
    (r'nueva apostolica', 'Nueva Apostólica', 'Cristiana'),
    (r'asamblea(s)? de dios', 'Asambleas de Dios', 'Cristiana'),
    (r'bautista', 'Bautista', 'Cristiana'),
    (r'luteran', 'Luterana', 'Cristiana'),
    (r'metodista', 'Metodista', 'Cristiana'),
    (r'anglican', 'Anglicana', 'Cristiana'),
    (r'presbiterian|reformada', 'Presbiteriana / Reformada', 'Cristiana'),
    (r'menonita', 'Menonita', 'Cristiana'),
    (r'ejercito de salvacion', 'Ejército de Salvación', 'Cristiana'),
    (r'cuadrangular', 'Evangelio Cuadrangular', 'Cristiana'),
    (r'universal del reino de dios', 'Iglesia Universal del Reino de Dios', 'Cristiana'),
    (r'hermanos libres|asamblea cristiana\b', 'Hermanos Libres / Asamblea Cristiana', 'Cristiana'),
    (r'iglesia de dios\b', 'Iglesia de Dios', 'Cristiana'),
    (r'pentecost|avivamiento|carismatic', 'Pentecostal', 'Cristiana'),
    (r'ortodox', 'Ortodoxa', 'Cristiana'),
    (r'catolic|parroquia|diocesis|arzobispado|obispado|capilla|basilica|catedral|nuestra senora|san (jose|pedro|pablo|juan|miguel|francisco|antonio|roque|cayetano|martin|lorenzo|nicolas|expedito)|santa (rosa|teresa|rita|lucia|ana|maria|clara|barbara|catalina)|sagrado corazon|inmaculada|cristo rey\b', 'Católica', 'Cristiana'),
    (r'evangeli|cristian|biblic|misioner|ministerio|apostolic|centro de fe|casa de oracion|rey de reyes|jesucristo|cristo\b|jesus\b|dios\b|senor\b|espiritu santo|gracia|betel|sion|shalom|siloe|siloh|rhema|maranata|jehova', 'Evangélica', 'Cristiana'),
    (r'judi|israelita|hebre|sinagoga|sefarad|ashkenaz|jabad|lubavitch|kehila|templo de la comunidad', 'Judía', 'Judía'),
    (r'islam|musulman|mezquita|arabe argentin', 'Musulmana', 'Musulmana'),
    (r'budis|budist|zen\b|soka gakkai|tibetan', 'Budista', 'Budista'),
    (r'hind|vaisnava|krishna|yoga vedanta|brahma kumaris', 'Hinduista', 'Hinduista'),
    (r"bahai|baha'i", "Bahá'í", "Bahá'í"),
    (r'espiritist|basilio|espiritual', 'Espiritista', 'Espiritista'),
    (r'umbanda|africanist|afro|batuque|quimbanda|kimbanda|orixa|orisha|yoruba|ifa\b', 'Afroamericana (umbanda / africanista)', 'Religiones afroamericanas'),
    (r'gauchito gil|difunta correa|san la muerte|religiosidad popular', 'Religiosidad popular', 'Religiosidad popular'),
]
ig = json.load(open(sys.argv[1], encoding='utf-8')); n = 0
for i in ig:
    if i.get('denominacion'): continue
    t = norm(i['entidad'] + ' ' + i['nombre'])
    for pat, den, rel in REGLAS:
        if re.search(pat, t): i['denominacion'] = den; i['religion'] = i.get('religion') or rel; n += 1; break
json.dump(ig, open(sys.argv[1], 'w', encoding='utf-8'), ensure_ascii=False, indent=0)
import collections; print(n, 'inferidas'); print(collections.Counter(i.get('denominacion') for i in ig).most_common(25))
