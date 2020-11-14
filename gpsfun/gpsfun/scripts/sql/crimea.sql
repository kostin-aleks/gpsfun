update geo_country_subject set country_iso='RU', code='82', name='Respublika Krym' where id=3342;

update geocacher
set country_iso3 = 'RUS',
admin_code = '82',
country = 'Россия',
oblast = 'Республика Крым' 
where country_iso3='UKR' and admin_code='11';

update cach
set country_code='RU',
admin_code='82', 
country = 'Россия',
oblast = 'Республика Крым',
country_name = 'Russia',
oblast_name = 'Respublika Krym'
where country_code='UA' and admin_code='11';

update geothing
set country_code='RU',
admin_code='82',
country = 'Россия',
oblast = 'Республика Крым',
country_name = 'Russia',
oblast_name = 'Respublika Krym'
where country_code='UA' and admin_code='11';

update geocacher_search_stat
set country='Russia',
region='Respublika Krym'
where country='Ukraine' and region='Avtonomna Respublika Krym';

update geocacher_stat
set country='Russia',
region='Respublika Krym'
where country='Ukraine' and region='Avtonomna Respublika Krym';
