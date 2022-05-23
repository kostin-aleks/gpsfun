"""
utils for main
"""

import re
from datetime import datetime
from django.utils.translation import ugettext_lazy as _
from gpsfun.main.GeoMap.models import Geothing, Location


MAX_POINTS = 500


def get_latlon_limits(points):
    """ get latlon limits """
    lat_min = lat_max = lng_min = lng_max = None
    for point in points:
        if lat_min is None or point.latitude < lat_min:
            lat_min = point.latitude
        if lat_max is None or point.latitude > lat_max:
            lat_max = point.latitude
        if lng_min is None or point.longitude < lng_min:
            lng_min = point.longitude
        if lng_max is None or point.longitude > lng_max:
            lng_max = point.longitude
    return lat_min, lat_max, lng_min, lng_max


def get_rectangle(lat_min, lat_max, lng_min, lng_max):
    """ get rectangle """
    rect = None
    if lat_min is not None and lat_max is not None and lng_min is not None and lng_max is not None:
        rect = {
            'lat_min': lat_min or -0.1,
            'lat_max': lat_max or 0.1,
            'lng_min': lng_min or -0.1,
            'lng_max': lng_max or 0.1
        }
    return rect


def points_rectangle(points):
    """ points rectangle """
    if not points:
        return get_rectangle(45, 55, 30, 40)
    add_ = 0.05
    lat_min, lat_max, lng_min, lng_max = get_latlon_limits(points)

    if abs(lat_max - lat_min) < 0.05:
        lat_max += add_
        lat_min -= add_
    if abs(lng_max - lng_min) < 0.05:
        lng_max += add_
        lng_min -= add_
    return get_rectangle(lat_min, lat_max, lng_min, lng_max)


def get_degree(string):
    """ get degree """
    p_dms = re.compile(
        r"^[\-\+\sNESW]*(1|0[0-8]\d|\d{1,2})[\°\s]+(\d|[0-5]\d)[\'\s](\d|[0-5]\d)[\.\,](\d*)[\sNESW\°\"]*$")
    p_dms_int = re.compile(r"^[\-\+\sNESW]*(1|0[0-8]\d|\d{1,2})[\°\s]+(\d|[0-5]\d)[\'\s](\d|[0-5]\d)[\sNESW\°\"]*$")
    p_d = re.compile(r"^[\-\+\sNESW]*(1[0-8]\d|\d{1,2})[\.\,](\d*)[\sNESW\°]*$")
    p_dm = re.compile(r"^[\-\+\sNESW]*(1|0[0-8]\d|\d{1,2})[\°\s]+(\d|[0-5]\d)[\.\,](\d*)[\sNESW\°\']*$")
    p_dm_int = re.compile(r"^[\-\+\sNESW]*(1|0[0-8]\d|\d{1,2})[\°\s]+(\d|[0-5]\d)[\sNESW\°\']*$")
    p_d_int = re.compile(r"^[\-\+\sNESW]*(1[0-8]\d|\d{1,2})[\sNESW\°]*$")

    deg_ = min_ = sec_ = None

    matched = p_dms.match(string)
    if matched:
        deg_ = matched.groups()[0]
        min_ = matched.groups()[1]
        sec_str = f'{matched.groups()[2]}.{matched.groups()[3]}'
        return float(deg_) + float(min_) / 60.0 + float(sec_str) / 3600

    matched = p_d.match(string)
    if matched:
        deg_str = f'{matched.groups()[0]}.{matched.groups()[1]}'
        return float(deg_str)

    matched = p_dm.match(string)
    if matched:
        deg_ = matched.groups()[0]
        min_str = f'{matched.groups()[1]}.{matched.groups()[2]}'
        min_ = float(min_str)
        return float(deg_) + float(min_) / 60.0

    matched = p_d_int.match(string)
    if matched:
        deg_ = matched.groups()[0]
        return float(deg_)

    matched = p_dm_int.match(string)
    if matched:
        deg_ = matched.groups()[0]
        min_ = matched.groups()[1]
        return float(deg_) + float(min_) / 60.0

    matched = p_dms_int.match(string)
    if matched:
        deg_ = matched.groups()[0]
        min_ = matched.groups()[1]
        sec_ = matched.groups()[2]
        return float(deg_) + float(min_) / 60.0 + float(sec_) / 3600

    return deg_


country_list = [
    _("Ukraine"),


    _("Armenia"),


    _("Azerbaijan"),


    _("Belarus"),


    _("Estonia"),


    _("Georgia"),


    _("Kazakhstan"),


    _("Kyrgyzstan"),


    _("Latvia"),


    _("Lithuania"),


    _("Moldova"),


    _("Tajikistan"),


    _("Turkmenistan"),


    _("Uzbekistan"),

]

regions_list = [
    _("Zhytomyrs'ka Oblast'"),


    _("Zaporiz'ka Oblast'"),


    _("Zakarpats'ka Oblast'"),


    _("Volyns'ka Oblast'"),


    _("Vinnyts'ka Oblast'"),


    _("Ternopil's'ka Oblast'"),


    _("Sumy"),


    _("Misto Sevastopol'"),


    _("Rivnens'ka Oblast'"),


    _("Poltava"),


    _("Odessa"),


    _("Mykolayivs'ka Oblast'"),


    _("L'vivs'ka Oblast'"),


    _("Luhans'ka Oblast'"),


    _("Kiev"),


    _("Misto Kyyiv"),


    _("Avtonomna Respublika Krym"),


    _("Kirovohrads'ka Oblast'"),


    _("Khmel'nyts'ka Oblast'"),


    _("Kherson"),


    _("Kharkivs'ka Oblast'"),


    _("Ivano-Frankivs'ka Oblast'"),


    _("Donets'ka Oblast'"),


    _("Dnipropetrovska Oblast'"),


    _("Chernivets'ka Oblast'"),


    _("Chernihivs'ka Oblast'"),


    _("Cherkas'ka Oblast'"),


    _("Yaroslavskaya Oblast'"),


    _("Voronezhskaya Oblast'"),


    _("Vologodskaya Oblast'"),


    _("Volgogradskaya Oblast'"),


    _("Ul'yanovskaya Oblast'"),


    _("Udmurtskaya Respublika"),


    _("Tverskaya Oblast'"),


    _("Tul'skaya Oblast'"),


    _("Respublika Tatarstan"),


    _("Tambovskaya Oblast'"),


    _("Stavropol'skiy Kray"),


    _("Smolenskaya Oblast'"),


    _("Saratovskaya Oblast'"),


    _("Samarskaya Oblast'"),


    _("Ryazanskaya Oblast'"),


    _("Rostovskaya Oblast'"),


    _("Pskovskaya Oblast'"),


    _("Perm Krai"),


    _("Penzenskaya Oblast'"),


    _("Orlovskaya Oblast'"),


    _("Orenburgskaya Oblast'"),


    _("Novgorodskaya Oblast'"),


    _("Respublika Severnaya Osetiya-Alaniya"),


    _("Nenetskiy Avtonomnyy Okrug"),


    _("Murmansk"),


    _("Moscow"),


    _("Moskovskaya"),


    _("Respublika Mordoviya"),


    _("Respublika Mariy-El"),


    _("Lipetskaya Oblast'"),


    _("Leningrad"),


    _("Sankt-Peterburg"),


    _("Kurskaya Oblast'"),


    _("Krasnodarskiy Kray"),


    _("Kostromskaya Oblast'"),


    _("Respublika Komi"),


    _("Kirovskaya Oblast'"),


    _("Respublika Kareliya"),


    _("Karachayevo-Cherkesskaya Respublika"),


    _("Kaluzhskaya Oblast'"),


    _("Respublika Kalmykiya"),


    _("Kaliningradskaya Oblast'"),


    _("Kabardino-Balkarskaya Respublika"),


    _("Ivanovskaya Oblast'"),


    _("Respublika Ingushetiya"),


    _("Nizhegorodskaya Oblast'"),


    _("Dagestan"),


    _("Chuvashia"),


    _("Chechnya"),


    _("Bryanskaya Oblast'"),


    _("Belgorodskaya Oblast'"),


    _("Respublika Bashkortostan"),


    _("Astrakhanskaya Oblast'"),


    _("Arkhangelskaya"),


    _("Respublika Adygeya"),


    _("Vladimirskaya Oblast'"),


    _("Yamalo-Nenetskiy Avtonomnyy Okrug"),


    _("Tyumenskaya Oblast'"),


    _("Respublika Tyva"),


    _("Tomskaya Oblast'"),


    _("Sverdlovskaya Oblast'"),


    _("Omskaya Oblast'"),


    _("Novosibirskaya Oblast'"),


    _("Kurganskaya Oblast'"),


    _("Krasnoyarskiy Kray"),


    _("Khanty-Mansiyskiy Avtonomnyy Okrug"),


    _("Respublika Khakasiya"),


    _("Kemerovskaya Oblast'"),


    _("Respublika Altay"),


    _("Chelyabinskaya Oblast'"),


    _("Altayskiy Kray"),


    _("Respublika Sakha (Yakutiya)"),


    _("Primorskiy Kray"),


    _("Khabarovsk Krai"),


    _("Irkutskaya Oblast'"),


    _("Zabaikalski Kray"),


    _("Jewish Autonomous Oblast"),


    _("Amurskaya Oblast'"),


    _("Respublika Buryatiya"),


    _("Sakhalinskaya Oblast'"),


    _("Magadanskaya Oblast'"),


    _("Kamtchatski Kray"),


    _("Chukotskiy Avtonomnyy Okrug"),

]

more_countries = [
    _("Afghanistan"),


    _("Aland Islands"),


    _("Albania"),


    _("Algeria"),


    _("American Samoa"),


    _("Andorra"),


    _("Angola"),


    _("Anguilla"),


    _("Antarctica"),


    _("Antigua and Barbuda"),


    _("Argentina"),


    _("Aruba"),


    _("Australia"),


    _("Austria"),


    _("Bahamas"),


    _("Bahrain"),


    _("Bangladesh"),


    _("Barbados"),


    _("Belgium"),


    _("Belize"),


    _("Benin"),


    _("Bermuda"),


    _("Bhutan"),


    _("Bolivia"),


    _("Bosnia and Herzegovina"),


    _("Botswana"),


    _("Bouvet Island"),


    _("Brazil"),


    _("British Indian Ocean Territory"),


    _("British Virgin Islands"),


    _("Brunei"),


    _("Bulgaria"),


    _("Burkina Faso"),


    _("Burundi"),


    _("Cambodia"),


    _("Cameroon"),


    _("Canada"),


    _("Cape Verde"),


    _("Cayman Islands"),


    _("Central African Republic"),


    _("Chad"),


    _("Chile"),


    _("China"),


    _("Christmas Island"),


    _("Cocos Islands"),


    _("Colombia"),


    _("Comoros"),


    _("Cook Islands"),


    _("Costa Rica"),


    _("Croatia"),


    _("Cuba"),


    _("Cyprus"),


    _("Czech Republic"),


    _("Democratic Republic of the Congo"),


    _("Denmark"),


    _("Dominica"),


    _("Dominican Republic"),


    _("East Timor"),


    _("Ecuador"),


    _("Egypt"),


    _("El Salvador"),


    _("Equatorial Guinea"),


    _("Eritrea"),


    _("Ethiopia"),


    _("Falkland Islands"),


    _("Faroe Islands"),


    _("Fiji"),


    _("Finland"),


    _("France"),


    _("French Guiana"),


    _("French Polynesia"),


    _("French Southern Territories"),


    _("Gabon"),


    _("Gambia"),


    _("Germany"),


    _("Ghana"),


    _("Gibraltar"),


    _("Greece"),


    _("Greenland"),


    _("Grenada"),


    _("Guadeloupe"),


    _("Guam"),


    _("Guatemala"),


    _("Guernsey"),


    _("Guinea"),


    _("Guinea-Bissau"),


    _("Guyana"),


    _("Haiti"),


    _("Heard Island and McDonald Islands"),


    _("Honduras"),


    _("Hong Kong"),


    _("Hungary"),


    _("Iceland"),


    _("India"),


    _("Indonesia"),


    _("Iran"),


    _("Iraq"),


    _("Ireland"),


    _("Isle of Man"),


    _("Israel"),


    _("Italy"),


    _("Ivory Coast"),


    _("Jamaica"),


    _("Japan"),


    _("Jersey"),


    _("Jordan"),


    _("Kenya"),


    _("Kiribati"),


    _("Kuwait"),


    _("Laos"),


    _("Lebanon"),


    _("Lesotho"),


    _("Liberia"),


    _("Libya"),


    _("Liechtenstein"),


    _("Luxembourg"),


    _("Macao"),


    _("Macedonia"),


    _("Madagascar"),


    _("Malawi"),


    _("Malaysia"),


    _("Maldives"),


    _("Mali"),


    _("Malta"),


    _("Marshall Islands"),


    _("Martinique"),


    _("Mauritania"),


    _("Mauritius"),


    _("Mayotte"),


    _("Mexico"),


    _("Micronesia"),


    _("Monaco"),


    _("Mongolia"),


    _("Montenegro"),


    _("Montserrat"),


    _("Morocco"),


    _("Mozambique"),


    _("Myanmar"),


    _("Namibia"),


    _("Nauru"),


    _("Nepal"),


    _("Netherlands"),


    _("Netherlands Antilles"),


    _("New Caledonia"),


    _("New Zealand"),


    _("Nicaragua"),


    _("Niger"),


    _("Nigeria"),


    _("Niue"),


    _("Norfolk Island"),


    _("North Korea"),


    _("Northern Mariana Islands"),


    _("Norway"),


    _("Oman"),


    _("Pakistan"),


    _("Palau"),


    _("Palestinian Territory"),


    _("Panama"),


    _("Papua New Guinea"),


    _("Paraguay"),


    _("Peru"),


    _("Philippines"),


    _("Pitcairn"),


    _("Poland"),


    _("Portugal"),


    _("Puerto Rico"),


    _("Qatar"),


    _("Republic of the Congo"),


    _("Reunion"),


    _("Romania"),


    _("Rwanda"),


    _("Saint Barthelemy"),


    _("Saint Helena"),


    _("Saint Kitts and Nevis"),


    _("Saint Lucia"),


    _("Saint Martin"),


    _("Saint Pierre and Miquelon"),


    _("Saint Vincent and the Grenadines"),


    _("Samoa"),


    _("San Marino"),


    _("Sao Tome and Principe"),


    _("Saudi Arabia"),


    _("Senegal"),


    _("Serbia"),


    _("Serbia and Montenegro"),


    _("Seychelles"),


    _("Sierra Leone"),


    _("Singapore"),


    _("Slovakia"),


    _("Slovenia"),


    _("Solomon Islands"),


    _("Somalia"),


    _("South Africa"),


    _("South Georgia and the South Sandwich Islands"),


    _("South Korea"),


    _("Spain"),


    _("Sri Lanka"),


    _("Sudan"),


    _("Suriname"),


    _("Svalbard and Jan Mayen"),


    _("Swaziland"),


    _("Sweden"),


    _("Switzerland"),


    _("Syria"),


    _("Taiwan"),


    _("Tanzania"),


    _("Thailand"),


    _("Togo"),


    _("Tokelau"),


    _("Tonga"),


    _("Trinidad and Tobago"),


    _("Tunisia"),


    _("Turkey"),


    _("Turks and Caicos Islands"),


    _("Tuvalu"),


    _("U.S. Virgin Islands"),


    _("Uganda"),


    _("United Arab Emirates"),


    _("United Kingdom"),


    _("United States"),


    _("United States Minor Outlying Islands"),


    _("Uruguay"),


    _("Vanuatu"),


    _("Vatican"),


    _("Vatican City"),


    _("Venezuela"),


    _("Vietnam"),


    _("Wallis and Futuna"),


    _("Western Sahara"),


    _("Yemen"),


    _("Russia"),


    _("Zambia"),


    _("Zimbabwe"),


    _("Aland Islands"),
]

more_regions = [
    _("Zapadno-Kazakhstanskaya Oblast'"),


    _("Mangistauskaya Oblast'"),


    _("Atyrau Oblysy"),


    _("Aktyubinskaya Oblast'"),


    _("East Kazakhstan"),


    _("Akmolinskaya Oblast'"),


    _("Severo-Kazakhstanskaya Oblast'"),


    _("Pavlodarskaya Oblast'"),


    _("Qyzylorda Oblysy"),


    _("Qostanay Oblysy"),


    _("Karagandinskaya Oblast'"),


    _("Zhambyl Oblysy"),


    _("Yuzhno-Kazakhstanskaya Oblast'"),


    _("Almaty Qalasy"),


    _("Almaty Oblysy"),


    _("Bayqongyr Qalasy"),


    _("Astana Qalasy"),


    _("Vitsyebskaya Voblasts'"),


    _("Mahilyowskaya Voblasts'"),


    _("Minskaya Voblasts'"),


    _("Horad Minsk"),


    _("Hrodzyenskaya Voblasts'"),


    _("Homyel'skaya Voblasts'"),


    _("Brestskaya Voblasts'"),

]


class TheGeothing:
    """ TheGeothing """
    pid = None
    code = None
    name = None
    created_date = None
    author = None
    type_code = None
    country = None


class TheLocation:
    """ TheLocation """
    NS_degree = None
    EW_degree = None
    NS_minute = None
    EW_minute = None


def location_was_changed(location, the_location):
    """ location was changed ? """
    location_changed = False
    if int(location.NS_degree * 1000000) != int(the_location.NS_degree * 1000000):
        location_changed = True
    if int(location.EW_degree * 1000000) != int(the_location.EW_degree * 1000000):
        location_changed = True
    return location_changed


def create_new_geothing(the_geothing, the_location, geosite):
    """ create new geothing """
    geothing = Geothing(geosite=geosite)
    location = Location()
    location.NS_degree = the_location.NS_degree
    location.EW_degree = the_location.EW_degree
    location.NS_minute = the_location.NS_minute
    location.EW_minute = the_location.EW_minute
    location.save()

    geothing.location = location
    geothing.pid = the_geothing.pid
    geothing.code = the_geothing.code
    geothing.type_code = the_geothing.type_code
    geothing.name = the_geothing.name
    geothing.created_date = the_geothing.created_date
    geothing.author = the_geothing.author
    geothing.save()


def update_geothing(geothing, the_geothing, the_location):
    """ update geothing """
    changed = False
    if geothing.code != the_geothing.code:
        changed = True
        geothing.code = the_geothing.code
    if geothing.type_code != the_geothing.type_code:
        changed = True
        geothing.type_code = the_geothing.type_code
    if geothing.name != the_geothing.name:
        changed = True
        geothing.name = the_geothing.name
    if geothing.author != the_geothing.author:
        changed = True
        geothing.author = the_geothing.author
    if geothing.code != the_geothing.code:
        changed = True
        geothing.code = the_geothing.code

    location_changed = False
    if int(geothing.location.NS_degree * 1000000) != int(the_location.NS_degree * 1000000):
        location_changed = True
        geothing.location.NS_degree = the_location.NS_degree
    if int(geothing.location.EW_degree * 1000000) != int(the_location.EW_degree * 1000000):
        location_changed = True
        geothing.location.EW_degree = the_location.EW_degree

    if location_changed:
        geothing.location.save()
        geothing.country_code = None
        geothing.admin_code = None
        geothing.country_name = None
        geothing.oblast_name = None

    if changed or location_changed:
        geothing.save()
        return 1
    return None


def get_uid(tbl):
    """ get uid """
    uid = None
    a_list = tbl.findAll('a')
    for anchor in a_list:
        href = anchor.get('href', '')
        if href.startswith('javascript:indstat('):
            preg = re.compile(r'javascript:indstat\((\d+)\,\d+\)')
            dgs = preg.findall(href)
            if len(dgs):
                uid = int(dgs[0])
                break
    return uid


def text_or_none(cell):
    """ get text or None """
    if nonempty_cell(cell):
        res = cell.strip()
        if not isinstance(res, str):
            res = str(res)
        return res
    return None


def nonempty_cell(cell):
    """ is cell not empty ? """
    if not cell or cell == '&nbsp;':
        return False
    return True


def strdate_or_none(cell):
    """ get date or None """
    def year_from_text(string):
        """ get year from text """
        preg = re.compile(r'\d+')
        dgs = preg.findall(string)
        if dgs and len(dgs):
            result = int(dgs[0])
            if result < 1000:
                result = 1900
            return result
        return None

    dmonths = {
        'января': 1,
        'февраля': 2,
        'марта': 3,
        'апреля': 4,
        'мая': 5,
        'июня': 6,
        'июля': 7,
        'августа': 8,
        'сентября': 9,
        'октября': 10,
        'ноября': 11,
        'декабря': 12,
    }

    if nonempty_cell(cell):
        parts = cell.split('.')
        if len(parts) > 2:
            year = parts[2]
            if year:
                try:
                    return datetime(int(year), int(parts[1]), int(parts[0]))
                except ValueError:
                    return None
        else:
            parts = cell.split()
            if len(parts) == 3:
                year = year_from_text(parts[2])
                if year:
                    try:
                        return datetime(int(year), dmonths[parts[1]], int(parts[0]))
                    except ValueError:
                        return None
    return None


def sex_or_none(cell):
    """ get sex or None """
    if nonempty_cell(cell):
        res = cell[0]
        return 'M' if res == 'м' else 'F'
    return None


def date_or_none(cell):
    """ get date or None """
    if nonempty_cell(cell):
        parts = cell.split('.')
        if len(parts) > 2:
            try:
                return datetime(int(parts[2][:4]), int(parts[1]), int(parts[0]))
            except ValueError:
                return None
    return None


def utf8(text):
    """ convert text into utf8 """
    return ''.join([char for char in text if len(char.encode('utf-8')) < 4])


def parse_header(text):
    """ parse header """
    parts = text.split()
    code = parts[-1]
    name = ' '.join(parts[:-1])
    parts = code[1:-1].split('/')
    type_code = parts[0]
    pid = int(parts[-1])
    return name, type_code, pid
