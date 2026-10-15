#!/usr/bin/env python3
"""Infiere denominación y religión a partir del nombre de la entidad, para las fichas que no la tienen."""
import json, re, sys, unicodedata
import os, sys
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from datos import cargar, guardar
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
# Valores crudos de OSM (inglés o variantes) -> denominación canónica. Lo que no está acá y no es canónico se descarta y se re-infiere.
CANON = {d for _, d, _ in REGLAS} | {'Católica', 'Evangélica', 'Pentecostal'}
TRAD = {'catholic':'Católica','roman catholic':'Católica','folk catholicism':'Religiosidad popular','greek catholic':'Católica','ukrainian greek catholic':'Católica','maronite':'Católica','institucion de religion catolica':'Católica','parroquia':'Católica','basilica':'Católica','capilla':'Católica',
 'evangelical':'Evangélica','evangelical christian':'Evangélica','cristiana evangelica':'Evangélica','crstiana evangelica':'Evangélica','christian':'Evangélica','cristiana':'Evangélica','protestant':'Protestante','protestante':'Protestante','neo pentecostal':'Pentecostal','charismatic':'Pentecostal','carismatic':'Pentecostal','apostolic':'Pentecostal','profetica apostolica':'Pentecostal','apostolic assembly of the faith in christ jesus':'Pentecostal','la luz del mundo':'La Luz del Mundo',
 'baptist':'Bautista','bautista independiente':'Bautista','lutheran':'Luterana','evangelical lutheran':'Luterana','methodist':'Metodista','metodista calvinista':'Metodista','anglican':'Anglicana','presbyterian':'Presbiteriana / Reformada','presbiteriana':'Presbiteriana / Reformada','presbiteriana reformada':'Presbiteriana / Reformada','reformed':'Presbiteriana / Reformada','reformada':'Presbiteriana / Reformada','reform':'Judía','congregational':'Congregacionalista','congregacionalista':'Congregacionalista','disciples of christ':'Discípulos de Cristo','quaker':'Cuáquera','unionista':'Evangélica','mennonite':'Menonita','salvation army':'Ejército de Salvación',
 'mormon':'Iglesia de Jesucristo de los Santos de los Últimos Días','latter day saints':'Iglesia de Jesucristo de los Santos de los Últimos Días','iglesia de los santos de los ultimos dias':'Iglesia de Jesucristo de los Santos de los Últimos Días','jehovahs witness':'Testigos de Jehová','seventh day adventist':'Adventista del Séptimo Día','adventist':'Adventista del Séptimo Día','new apostolic':'Nueva Apostólica','iglesia nueva apostolica':'Nueva Apostólica','assemblies of god':'Asambleas de Dios','union de las asambleas de dios':'Asambleas de Dios','universal':'Iglesia Universal del Reino de Dios',
 'orthodox':'Ortodoxa','russian orthodox':'Ortodoxa','romanian orthodox':'Ortodoxa','greek orthodox':'Ortodoxa','armenian apostolic':'Ortodoxa','bizantino ucraniana':'Católica',
 'jewish':'Judía','jude':'Judía','judia':'Judía','judia conservadora':'Judía','orthodox jewish':'Judía','conservative':'Judía','lubavitch':'Judía','jabad lubavitch':'Judía',
 'muslim':'Musulmana','sunni':'Musulmana','shia':'Musulmana','musulmana sunita':'Musulmana','musulmana chiita':'Musulmana',
 'buddhist':'Budista','tibetan':'Budista','nichiren':'Budista','new kadampa tradition':'Budista','zen':'Budista','hindu':'Hinduista','bahai':"Bahá'í",'baha i':"Bahá'í",'instituto bahai':"Bahá'í",'spiritualist':'Espiritista','religiosa':None,'fixme':None,'retiros':None,'la gruta':None,'gruta de la virgen':'Católica','cita con la vida':'Evangélica'}
ig = cargar(sys.argv[1]); n = 0
for i in ig:
    d = i.get('denominacion')
    if d and d not in CANON:
        k = norm(d).replace('-', ' ').replace('_', ' ').strip()
        i['denominacion'] = TRAD.get(k) if (k in TRAD or len(k.split()) <= 4) else None
        if i['denominacion'] is None and k in TRAD: pass
        elif i['denominacion'] is None and k not in TRAD: i['denominacion'] = None
    if i.get('denominacion'): continue
    t = norm(i['entidad'] + ' ' + i['nombre'])
    for pat, den, rel in REGLAS:
        if re.search(pat, t): i['denominacion'] = den; i['religion'] = i.get('religion') or rel; n += 1; break
guardar(sys.argv[1], ig)
import collections; print(n, 'inferidas'); print(collections.Counter(i.get('denominacion') for i in ig).most_common(25))
