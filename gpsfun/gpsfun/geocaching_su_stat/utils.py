import operator
import re
import requests
from datetime import datetime
from bs4 import BeautifulSoup
from gpsfun.DjHDGutils.dbutils import get_object_or_none
from gpsfun.main.GeoCachSU.models import Geocacher, Cach
from gpsfun.main.utils import (
    date_or_none, sex_or_none, strdate_or_none, utf8)


LOGIN_DATA = {
    'Log_In': 'Log_In',
    'email': 'galdor@ukr.net',
    'passwd': 'zaebalixakeryvas',
    'x': 8, 'y': 8
}

USER_NAME = 'galdor'


def logged(text):
    soup = BeautifulSoup(text, 'html.parser')
    a = soup.findAll(
        'a', class_='profilelink', text='galdor')

    return a is not None


def get_user_profile(uid, text):
    geocacher = None
    soup = BeautifulSoup(text, 'lxml')

    table = soup.find('table', class_='pages')
    user = {'uid': uid}
    if table:
        rows = table.find_all('tr')
        for row in rows:
            title_cell = row.find('td')
            data_cells = row.find_all('th')
            if title_cell and data_cells:
                title = title_cell.text
                data = data_cells[-1].text
                if title.startswith('Псевдоним:'):
                    user['nickname'] = utf8(data)
                    continue
                if title.startswith('Страна:'):
                    user['country'] = data
                    continue
                if title.startswith('Область:'):
                    user['oblast'] = data
                    continue
                if title.startswith('Нас.пункт'):
                    user['town'] = data
                    continue
                if title.startswith('Создал тайников:'):
                    user['created'] = data
                    continue
                if title.startswith('Нашел тайников:'):
                    user['found'] = data
                    continue
                if title.startswith('Рекомендовал тайников:'):
                    user['recommended'] = data
                    continue
                if title.startswith('Фотоальбомы:'):
                    user['photo_albums'] = data
                    continue
                if title.startswith('Был на сайте'):
                    user['last_visited'] = data
                    continue
                if title.startswith('Дата регистрации:'):
                    user['registered'] = data
                    continue
                if title.startswith('Сообщений в форумах:'):
                    user['forum_posts'] = data
                if title.startswith('День рождения:'):
                    user['birstday'] = data
                    continue
                if title.startswith('Телефон:'):
                    user['phone'] = data
                    continue
                if title.startswith('Пол:'):
                    user['sex'] = data
                    continue
                if title.startswith('Настоящее'):
                    user['name'] = data
                    continue

        if int(user.get('found', 0)):
            geocacher, created = Geocacher.objects.get_or_create(
                uid=uid, nickname=user.get('nickname'))
            geocacher.name = user.get('name')
            geocacher.birstday = strdate_or_none(user.get('birstday'))
            geocacher.sex = sex_or_none(user.get('sex'))
            geocacher.country = user.get('country')
            geocacher.oblast = user.get('oblast')
            geocacher.town = user.get('town')
            geocacher.phone = user.get('phone')
            geocacher.created_caches = date_or_none(user.get('created'))
            geocacher.found_caches = user.get('found')
            geocacher.register_date = date_or_none(user.get('registered'))
            geocacher.last_login = date_or_none(user.get('last_visited'))
            geocacher.forum_posts = user.get('forum_posts')
            geocacher.save()

    return geocacher


def get_country_data(latitude, longitude):

    with requests.Session() as session:
        r = session.get(
            'http://api.geonames.org/countrySubdivision',
            params={
                'lat': latitude,
                'lng': longitude,
                'username': 'galdor'
            }
        )

        soup = BeautifulSoup(r.text, 'lxml')

        data = soup.geonames.countrysubdivision
        if data:
            return {
                'status': 'ok',
                'country_id': data.countrycode.text if data.countrycode else None,
                'country_name': data.countryname.text if data.countryname else None,
                'sub_id': data.admincode1.text if data.admincode1 else None,
                'sub_name': data.adminname1.text if data.adminname1 else None
            }
        else:
            data = soup.status
            if 'hourly limit' in data.get('message', ''):
                return {'status': 'limit'}
        return {}


def get_form_fields(text):
    POINTS_FIELD = 'point[]'
    soup = BeautifulSoup(text, 'lxml')
    form = soup.find('form')
    post_data = {POINTS_FIELD: []}
    if form:
        inputs = form.find_all('input')
        for input_ in inputs:
            if input_.get('name') and input_.get('value'):
                if input_['name'] == POINTS_FIELD:
                    post_data[POINTS_FIELD].append(input_['value'])
                else:
                    post_data[input_['name']] = input_['value']
        del post_data['translit']
        post_data['fmt'] = 'txt'
        post_data['finded'] = '1'
        post_data["countries"] = "on"
    return post_data


def get_caches(last_max_cid=None):

    CELL_COUNT = 10
    CODE = 2
    LATITUDE = 3
    LAT_MINUTES = 4
    LONGITUDE = 5
    LON_MINUTES = 6
    CREATED = 7
    NAME = -1

    cache_urls = []
    rows = []
    with requests.Session() as session:
        post = session.post(
            'https://geocaching.su',
            data=LOGIN_DATA,
        )

        r = session.get('https://geocaching.su')
        if not logged(r.text):
            print('Authorization failed')
        else:
            r = session.get(
                'http://www.geocaching.su/site/popup/selex.php',
            )
            post_data = get_form_fields(r.text)

            r = session.post(
                'https://geocaching.su/site/popup/export.php',
                data=post_data
            )
            rows = r.text.split('\r\n')

    for row in rows:
        c = {}
        items = row.split(',')
        if len(items) == CELL_COUNT:
            if items[0] == 'WP' and items[1] == 'DMX':
                code = items[CODE]
                c['type_code'] = re.search(r"^[A-Z]+", code).group(0)
                c['cid'] = re.search(r"\d+", code).group(0)
                c['code'] = code

                c['latitude'] = int(items[LATITUDE])
                c['lat_minutes'] = float(items[LAT_MINUTES])
                c['longitude'] = int(items[LONGITUDE])
                c['lon_minutes'] = float(items[LON_MINUTES])

                c['created'] = items[CREATED]

                text = items[NAME]
                words = text.split('от')
                c['author'] = words[-1].strip()
                c['name'] = ' от '.join(words[:-1])
                c['name'] = c['name'].strip()

                if last_max_cid is None or (int(c['cid'] or 0) > last_max_cid):
                    print('added', c)
                    cache, created = Cach.objects.get_or_create(
                        pid=c['cid'],
                    )
                    cache.type_code = c['type_code']
                    cache.code=c['code']
                    dt = datetime.strptime(c['created'], '%m/%d/%Y')
                    cache.created_date = dt
                    cache.latitude = float(c['latitude']) + c['lat_minutes'] / 60.0
                    cache.longitude = float(
                        c['longitude']) + c['lon_minutes'] / 60.0

                    cache.name = c['name']

                    cache.author = get_object_or_none(
                        Geocacher, nickname=c['author'])

                    #if cache.country_code is None:
                        #cache.country_code = get_country_code(
                            #cache.latitude, cache.longitude)

                    cache.save()


def get_caches_data(uid, text):
    data = []

    soup = BeautifulSoup(text, 'lxml')

    table = soup.find('table', class_='pages')

    if table:
        rows = table.find_all('tr')
        for row in rows:
            data_cell = row.find('td')
            if data_cell:
                anchor = data_cell.find_all('a')[-1]
                if anchor:
                    href = anchor['href']
                    items = href.split('=')
                    cid = items[-1]

                    text = data_cell.text
                    items = text.split(',')

                    grade_data = ''
                    found = items[-1].strip()
                    if found.startswith('оценен'):
                        grade_data = found
                        found = items[-2].strip()

                    found = found.split()[-1].strip()
                    found_date = date_or_none(found)

                    items = grade_data.split()
                    if len(items):
                        grade_data = items[-1].strip()
                    grade = int(grade_data) if grade_data.isdigit() else None

                    coauthor = '(соавтор' in text

                    if cid and cid.isdigit():
                        data.append((cid, found_date, grade, coauthor))

    return data


def get_geocachers_uids(text):
    uids = []

    soup = BeautifulSoup(text, 'lxml')

    table = soup.find('table', class_='pages')

    if table:
        rows = table.find_all('tr')
        for row in rows:
            row_id = row.get('id')
            if row_id and row_id.startswith('tr_'):
                cells = row.find_all('td')
                if cells and len(cells) > 1:
                    cell = cells[1]
                    anchor = cell.find('a')
                    if anchor:
                        href = anchor['onclick']
                        match = re.search(r"profile\.php\?uid\=(\d+)", href)
                        if match:
                            uid = match.group(1)
                            uids.append(uid)

    uids = list(set(uids))
    return uids


def set_country_code(uid, country):
    geocacher = Geocacher.objects.filter(uid=uid).first()
    if geocacher and geocacher.country_iso3 is None and country:
        if country == 'Россия':
            geocacher.country_iso3 = 'RUS'
            geocacher.save()
        elif country == 'Украина':
            geocacher.country_iso3 = 'UKR'
            geocacher.save()
        elif country == 'Беларусь':
            geocacher.country_iso3 = 'BLR'
            geocacher.save()
        elif country == 'Латвия':
            geocacher.country_iso3 = 'LVA'
            geocacher.save()


def set_oblast_code(uid, oblast):
    OBLAST = {
        'Абхазия': ['GEO', '02'],
        'Австрия': ['AUT', '777'],
        'Аджария': ['GEO', '04'],
        'Адыгея респ.': ['RUS', '01'],
        'Акмолинская обл.': ['KAZ', '03'],
        'Алтай респ.': ['RUS', '03'],
        'Алтайский край': ['RUS', '04'],
        'Амурская обл.': ['RUS', '05'],
        'Архангельская обл.': ['RUS', '06'],
        'Астраханская обл.': ['RUS', '07'],
        'Башкортостан респ.': ['RUS', '08'],
        'Белгородская обл.': ['RUS', '09'],
        'Болгария': ['BGR', '777'],
        'Брестская обл.': ['BLR', '01'],
        'Брянская обл.': ['RUS', '10'],
        'Бурятия респ.': ['RUS', '11'],
        'Великобритания': ['GBR', '777'],
        'Видземе': ['LVA', '01'],
        'Витебская обл.': ['BLR', '07'],
        'Владимирская обл.': ['RUS', '83'],
        'Волгоградская обл.': ['RUS', '84'],
        'Вологодская обл.': ['RUS', '85'],
        'Воронежская обл.': ['RUS', '86'],
        'Гегаркуник': ['ARM', '04'],
        'Германия': ['DEU', '777'],
        'Греция': ['GRC', '777'],
        'Гродненская обл.': ['BLR', '03'],
        'Днепропетровская обл.': ['UKR', '04'],
        'Донецкая обл.': ['UKR', '05'],
        'Египет': ['EGY', '777'],
        'Житомирская обл.': ['UKR', '27'],
        'Закарпатская обл.': ['UKR', '25'],
        'Запорожская обл.': ['UKR', '26'],
        'Ивановская обл.': ['RUS', '21'],
        'Израиль': ['ISR', '777'],
        'Имеретия': ['GEO', '66'],
        'Иркутская обл.': ['RUS', '20'],
        'Италия': ['ITA', '777'],
        'Калининградская обл.': ['RUS', '23'],
        'Калужская обл.': ['RUS', '25'],
        'Камчатский край': ['RUS', '92'],
        'Карачаево-Черкесская респ.': ['RUS', '27'],
        'Карелия респ.': ['RUS', '28'],
        'Кемеровская обл.': ['RUS', '29'],
        'Киевская обл.': ['UKR', '13'],
        'Кипр': ['CYP', '777'],
        'Кировская обл.': ['RUS', '33'],
        'Коми респ.': ['RUS', '34'],
        'Костромская обл.': ['RUS', '37'],
        'Краснодарский край': ['RUS', '38'],
        'Красноярский край': ['RUS', '91'],
        'Крым респ. и Севастополь': ['RUS', '82'],
        'Курганская обл.': ['RUS', '40'],
        'Курская обл.': ['RUS', '41'],
        'Латвия': ['LVA', '777'],
        'Липецкая обл.': ['RUS', '43'],
        'Луганская обл.': ['UKR', '14'],
        'Львовская обл.': ['UKR', '15'],
        'Ляэне-Вирумаа': ['EST', '08'],
        'Мангистауская обл.': ['KAZ', '09'],
        'Марий Эл респ.': ['RUS', '45'],
        'Минская обл.': ['BLR', '05'],
        'Могилевская обл.': ['BLR', '06'],
        'Молдова': ['MDA', '777'],
        'Мордовия респ.': ['RUS', '46'],
        'Москва и Московская обл.': ['RUS', '47'],
        'Мурманская обл.': ['RUS', '49'],
        'Мцхета-Мтианети': ['GEO', '69'],
        'Намибия': ['NAM', '777'],
        'Нижегородская обл.': ['RUS', '51'],
        'Николаевская обл.': ['UKR', '16'],
        'Новгородская обл.': ['RUS', '52'],
        'Новосибирская обл.': ['RUS', '53'],
        'Норвегия': ['NOR', '777'],
        'Одесская обл.': ['UKR', '17'],
        'Оренбургская обл.': ['RUS', '55'],
        'Орловская обл.': ['RUS', '56'],
        'Пензенская обл.': ['RUS', '57'],
        'Пермский край': ['RUS', '90'],
        'Полтавская обл.': ['UKR', '18'],
        'Польша': ['POL', '777'],
        'Приморский край': ['RUS', '59'],
        'Псковская обл.': ['RUS', '60'],
        'Ростовская обл.': ['RUS', '61'],
        'Румыния': ['ROU', '777'],
        'Рязанская обл.': ['RUS', '62'],
        'СПб и Ленинградская обл.': ['RUS', '42'],
        'Сааремаа': ['EST', '14'],
        'Самарская обл.': ['RUS', '65'],
        'Саратовская обл.': ['RUS', '67'],
        'Сахалинская обл.': ['RUS', '64'],
        'Свердловская обл.': ['RUS', '71'],
        'Северная Осетия респ.': ['RUS', '68'],
        'Словакия': ['SVK', '777'],
        'Смоленская обл.': ['RUS', '69'],
        'Ставропольский край': ['RUS', '70'],
        'Сумская обл.': ['UKR', '21'],
        'Таиланд': ['THA', '777'],
        'Тамбовская обл.': ['RUS', '72'],
        'Татарстан респ.': ['RUS', '73'],
        'Тверская обл.': ['RUS', '77'],
        'Тернопольская обл.': ['UKR', '22'],
        'Томская обл.': ['RUS', '75'],
        'Тульская обл.': ['RUS', '76'],
        'Турция': ['TUR', '777'],
        'Тыва (Тува': ['RUS', '79'],
        'Тюменская обл.': ['RUS', '78'],
        'Удмуртская респ.': ['RUS', '80'],
        'Ульяновская обл.': ['RUS', '81'],
        'Финляндия': ['FIN', '777'],
        'Хабаровский край': ['RUS', '30'],
        'Хакасия респ.': ['RUS', '31'],
        'Харьковская обл.': ['UKR', '07'],
        'Харьюмаа': ['EST', '01'],
        'Херсонская обл.': ['UKR', '08'],
        'Хмельницкая обл.': ['UKR', '09'],
        'Хорватия': ['HRV', '777'],
        'Челябинская обл.': ['RUS', '13'],
        'Черкасская обл.': ['UKR', '01'],
        'Черниговская обл.': ['UKR', '02'],
        'Черновицкая обл.': ['UKR', '03'],
        'Черногория': ['MNE', '777'],
        'Чехия': ['CZE', '777'],
        'Чувашская респ.': ['RUS', '16'],
        'Швейцария': ['CHE', '777'],
        'Швеция': ['SWE', '777'],
        'Ямало-Ненецкий авт. окр.': ['RUS', '87'],
        'Ярославская обл.': ['RUS', '88']}


    geocacher = Geocacher.objects.filter(uid=uid).first()
    if geocacher and geocacher.admin_code is None and oblast:
        o = OBLAST.get(oblast)
        if o:
            geocacher.country_iso3 = o[0]
            geocacher.admin_code = o[1]
            geocacher.save()


def get_found_caches_countries(uid, text):
    countries = []
    soup = BeautifulSoup(text, 'lxml')

    table = soup.find('table', class_='pages')
    if table:
        rows = table.find_all('tr')
        for row in rows:
            cell = row.find('td')
            if cell:
                match = re.search(r"(\(\d+.+\))", cell.text)
                if match:
                    s = match.group(1)
                    items = s.split(',')
                    if len(items):
                        country = items[-2].strip()
                        countries.append(country)
    d = {}
    for country in countries:
        d[country] = (d.get(country) or 0) + 1
    sorted_d = sorted(d.items(), key=operator.itemgetter(1), reverse=True)
    if sorted_d and sorted_d is list and sorted_d[0]:
            return sorted_d[0][0]


def get_found_caches_oblast(uid, text):
    oblasti = []
    soup = BeautifulSoup(text, 'lxml')

    table = soup.find('table', class_='pages')
    if table:
        rows = table.find_all('tr')
        for row in rows:
            cell = row.find('td')
            if cell:
                match = re.search(r"\((\d+\.\d+\.\d+\,\s+[^)]+)\)", cell.text)
                if match:
                    s = match.group(1)
                    items = s.split(',')
                    if len(items):
                        oblast = items[-1].strip()
                        oblasti.append(oblast)
    d = {}
    for oblast in oblasti:
        d[oblast] = (d.get(oblast) or 0) + 1
    sorted_d = sorted(d.items(), key=operator.itemgetter(1), reverse=True)
    if sorted_d and sorted_d is list and sorted_d[0]:
        return sorted_d[0][0]


def get_author(text):
    soup = BeautifulSoup(text, 'lxml')
    for div in soup.find_all('div'):
        t = div.text.strip()
        if t.startswith('Автор: '):
            anchor = div.find('a')
            href = anchor.get('onclick')
            match = re.search(r"profile.php\?uid\=(\d+)", href)
            if match:
                return match.groups(1)[0]

