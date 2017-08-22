#!/usr/bin/python2
# -*- coding: utf-8 -*-
from __future__ import division
from lxml import html
from bs4 import UnicodeDammit
import json, requests, urllib, os, re, csv

street_type = 'str1'
street = u'Якубовича'
house = u'20'

street_types = {
    'str1'  : u'Улица',
    'str2'  : u'Переулок',
    'str3'  : u'Проспект',
    'str4'  : u'Площадь',
    'str5'  : u'Микрорайон',
    'str6'  : u'Аллея',
    'str7'  : u'Бульвар',
    'str8'  : u'Аал',
    'str9'  : u'Аул',
    'str10' : u'Въезд',
    'str11' : u'Выселки',
    'str12' : u'Городок',
    'str13' : u'Деревня',
    'str14' : u'Дорога',
    'str15' : u'ж/д остановочный (обгонный) пункт',
    'str16' : u'Железнодорожная будка',
    'str17' : u'Железнодорожная казарма',
    'str18' : u'Железнодорожная платформа',
    'str19' : u'Железнодорожная станция',
    'str20' : u'Железнодорожный пост',
    'str21' : u'Железнодорожный разъезд',
    'str22' : u'Животноводческая точка',
    'str23' : u'Заезд',
    'str24' : u'Казарма',
    'str25' : u'Квартал',
    'str26' : u'Километр',
    'str27' : u'Кольцо',
    'str28' : u'Линия',
    'str29' : u'Местечко',
    'str30' : u'Набережная',
    'str31' : u'Населенный пункт',
    'str32' : u'Остров',
    'str33' : u'Парк',
    'str34' : u'Переезд',
    'str35' : u'Планировочный район',
    'str36' : u'Платформа',
    'str37' : u'Площадка',
    'str38' : u'Полустанок',
    'str39' : u'Поселок/станция',
    'str40' : u'Поселок сельского типа',
    'str41' : u'Починок',
    'str42' : u'Почтовое отделение',
    'str43' : u'Проезд',
    'str44' : u'Просек',
    'str45' : u'Проселок',
    'str46' : u'Проулок',
    'str47' : u'Разъезд',
    'str48' : u'Сад',
    'str49' : u'Село',
    'str50' : u'Сквер',
    'str51' : u'Слобода',
    'str52' : u'Станция',
    'str53' : u'Строение',
    'str54' : u'Территория',
    'str55' : u'Тракт',
    'str56' : u'Тупик',
    'str57' : u'Участок',
    'str58' : u'Хутор',
    'str59' : u'Шоссе'
}

payload = {
    "search_action":    "true",
    "subject":          "",
    "region":           "",
    "settlement":       "",
    "cad_num":          "",
    "start_position":   "59",
    "obj_num":          "",
    "old_number":       "",
    "search_type":      "ADDRESS",
    "subject_id":       "140000000000",
    "street_type":      street_type,
    "street":           street,
    "house":            house,
    "building":         "",
    "structure":        "",
    "apartment":        "",
    "right_reg":        "",
    "encumbrance_reg":  ""
}
baseURL  = ur'https://rosreestr.ru/wps/portal/p/cc_ib_portal_services/online_request/!ut/p/z1/04_Sj9CPykssy0xPLMnMz0vMAfIjo8zi3QNNXA2dTQy93QMNzQ0cPR29DY0N3Q0MQkz1w_Eq8DfUj6JEP1ABSL8BDuBoANQfhdcKZyMCCkBOJGxJZJR5vIGhh6Oho4mRt7uJi7GBo7FTaJiHsT9IiX5BbmiEQWZAJQAEJnXg/'
searchURL = baseURL + ur'p0/IZ7_01HA1A42KODT90AR30VLN22001=CZ6_GQ4E1C41KGQ170AIAK131G00T5=MEcontroller!QCPSearchAction==/'

rr_sess = requests.session()
rr_api_sess = requests.session()

house_path = "./rosreestr/" + street + " " + street_types[street_type].lower() + "/" + house 
if not os.path.exists(house_path):
    os.makedirs(house_path)

def parse_search( search_tree ):
  page = search_tree.xpath('//td[@class="brdw1111"]')[1]
  rows = page.xpath('.//tr[@valign="top"]')
  for link_xml in rows:
    link_href = link_xml.xpath('.//td[1]/a/@href')[0].strip()
    object_number = link_xml.xpath('.//td[2]/nobr/text() | .//td[3]/nobr/text()')[0].strip()
    apartment_path = house_path;
    #print urllib.quote_plus(object_number)
    r = rr_api_sess.get('https://rosreestr.ru/api/online/fir_objects/' + urllib.quote_plus(object_number))    
    if r.status_code == requests.codes.ok:
      for o in r.json():
        if street.upper().encode("utf-8").strip() in o["street"].encode("utf-8").strip():
          if o["apartment"]:
            apartment_path = house_path + u"/кв" + o["apartment"]
    data_path = apartment_path + "/" + object_number.replace('/',':')
    if not os.path.exists(data_path):
      os.makedirs(data_path)
    common_path = data_path + "/" + u'Общее.txt'
    rights_path = data_path + "/" + u'Права.txt'
    limits_path = data_path + "/" + u'Ограничения.txt'
    more_path = data_path + "/" + u'Отметки.txt'
    r = rr_sess.get(baseURL + link_href)
    tree = html.document_fromstring(r.content, parser=parser)
    data = parse_page(tree)
    rl = parse_rights(tree)
    m = parse_more(tree)
    sdata = ""
    if len(rl[0]) > 0:
      f = open(rights_path, 'w')
      for d in sorted(rl[0]):
        f.write(rl[0][d].encode("utf-8").strip() + "\n")
      f.close()
    if len(rl[1]) > 0:
      f = open(limits_path, 'w')
      for d in sorted(rl[1]):
        f.write(rl[1][d].encode("utf-8").strip() + "\n" )
      f.close()
    if len(m) > 0:
      f = open(more_path, 'w')
      f.write(m.encode("utf-8").strip())
      f.close()
    f = open(common_path, 'w')
    for key, value in data.items():
      sdata = sdata + '{} {}\n'.format(key.encode("utf-8").strip(), value.encode("utf-8").strip())
    f.write(sdata)
    f.close()
    if o["apartment"]:
      if data[u'(ОКС) Тип:'] == u'Квартира, Жилое помещение':
        lf_data.append([o["apartment"].encode("utf-8").strip(), data[u'Этаж:'].encode("utf-8").strip(), data[u"Площадь ОКС'a:"].encode("utf-8").strip(), data[u'Кадастровая стоимость:'].encode("utf-8").strip()])
    print data_path

def parse_page( page_tree ):
  page = page_tree.xpath('//td[@class="brdw1010"]')[0]
  rows = page.xpath('.//tr[not(@height)]')
  rdata = {}
  for row in rows:
    if row.xpath('.//td[1]/nobr/text()'):
      r_key = row.xpath('.//td[1]/nobr/text()')[0].strip()
    else:
      r_key = row.xpath('.//td[1]/text()')[0].strip()
    if row.xpath('.//td[2]/b/text()'):
      r_value = row.xpath('.//td[2]/b/text()')[0].strip()
    else:
      r_value = ''
    rdata[r_key] = r_value
  return rdata

def parse_rights( page_tree ):
  page = page_tree.xpath('//div[@id="r_enc"]')[0]
  rows = page.xpath('.//tr[@height="25px"]')
  rights = {}
  limits = {}
  n = 1
  for row in rows:
    right = row.xpath('.//td[1]/text()')[0].strip()
    if right != "":      
      right_r = right.split()
      date_r = right_r[3]
      date_s = date_r.split('.')
      date_s.reverse()
      rights[".".join(date_s) + "_" + str(n)] = date_r + " " + " ".join(right_r[4:]) + " " + right_r[1]
    if row.xpath('.//tr/td/text()'):
      limit = row.xpath('.//tr/td/text()')[0].strip()
      if limit != "":
        limit_r = limit.split()
        date_r = limit_r[3]
        date_s = date_r.split('.')
        date_s.reverse()
        limits[".".join(date_s) + "_" + str(n)] = date_r + " " + " ".join(limit_r[4:]) + " " + limit_r[1]
    n = n + 1
  return [rights, limits]

def parse_more( page_tree ):
  rmore = ''
  if page_tree.xpath('//div[@id="s_notes"]'):
    page = page_tree.xpath('//div[@id="s_notes"]')[0]
    rows = page.xpath('.//tr[@height="45px"]')    
    for row in rows:
      more = row.xpath('.//td/text()')[0].strip()
      if more != "":      
        rmore = rmore + more + "\n"
  return rmore

lf_data = []
r = rr_sess.post(searchURL, data=payload)
html_ud = UnicodeDammit(r.content, is_html=True)
parser = html.HTMLParser(encoding=html_ud.original_encoding)
tree = html.document_fromstring(r.content, parser=parser)
rows_number = int(tree.xpath('//div[@id="pg_stats"]/b[1]/text()')[0].strip())
pages_number = -(-rows_number // 20)
print 'Всего объектов: %d' %(rows_number)
parse_search(tree)
print "Получил страницу 1 из %d" %(pages_number)
if rows_number > 20:
  for pn in range(2, pages_number + 1):
    r = rr_sess.get(searchURL + ur'?online_request_search_page=' + str(pn) + ur'#Z7_01HA1A42KG4D30A3BUVH3O0000')
    tree = html.document_fromstring(r.content, parser=parser)
    parse_search(tree)
    print "Получил страницу %d из %d" %(pn, pages_number)
with open(house_path + u"/Квартиры.csv", "wb") as f:
    writer = csv.writer(f, quoting=csv.QUOTE_ALL)
    lf_data.sort(key=lambda x:int(x[0]))
    writer.writerow([u"Кв".encode('utf-8'), u"Эт".encode('utf-8'), u"Пл".encode('utf-8'), u"КС".encode('utf-8')])
    for row in lf_data:
      row=[s.encode('utf-8') for s in row]
      writer.writerows([row])
print house_path + u"/Квартиры.csv"
