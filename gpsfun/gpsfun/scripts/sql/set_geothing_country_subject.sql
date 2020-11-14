UPDATE geothing SET country_code='MU', country_name='Mauritius', admin_code='777', oblast_name='undefined subject' WHERE pid in (10926, 10811, 10924, 10767) and geosite_id=4;
UPDATE geothing SET country_code='ES', country_name='Spain', admin_code='53', oblast_name='Canary Islands' WHERE pid IN (6042, 6041, 6039, 6038) and geosite_id=4;
UPDATE geothing SET country_code='GB', country_name='United Kingdom', admin_code='ENG', oblast_name='England' WHERE pid=11778 and geosite_id=4;
UPDATE geothing SET country_code='PL', country_name='Poland', admin_code='777', oblast_name='undefined subject' WHERE pid IN (6736, 6713, 6730, 12988, 12364, 12365, 12362, 9051) and geosite_id=4;
UPDATE geothing SET country_code='GR', country_name='Greece', admin_code='777', oblast_name='undefined subject' WHERE pid IN (11026) and geosite_id=1;
UPDATE geothing SET country_code='ME', country_name='Montenegro', admin_code='777', oblast_name='undefined subject' WHERE pid IN (11270) and geosite_id=1;
UPDATE geothing SET country_code='BY', country_name='Belarus', admin_code='02', oblast_name='Homyel\'skaya Voblasts\'' WHERE pid IN (11137, 11197, 11172) and geosite_id=1;
UPDATE geothing SET country_code='ID', country_name='Indonesia', admin_code='02', oblast_name='Bali' WHERE pid IN (6292, 6116, 6115, 6113, 6112, 6110, 6104, 6092, 6091, 6089, 2443, 2407, 2390, 2216, 692) and geosite_id=2;
UPDATE geothing SET country_code='ID', country_name='Indonesia', admin_code='26', oblast_name='North Sumatra' WHERE pid IN (6249) and geosite_id=2;
UPDATE geothing SET country_code='LV', country_name='Latvia', admin_code='25', oblast_name='Riga' WHERE pid IN (1759, 1757, 1755, 1747, 1743, 1576) and geosite_id=2;
UPDATE geothing SET country_code='ME', country_name='Montenegro', admin_code='05', oblast_name='Opstina Budva' WHERE pid IN (1311, 1299) and geosite_id=2;
UPDATE geothing SET country_code='ME', country_name='Montenegro', admin_code='10', oblast_name='Opstina Kotor' WHERE pid IN (1300) and geosite_id=2;
UPDATE geothing SET country_code='ME', country_name='Montenegro', admin_code='08', oblast_name='Opstina Herceg Novi' WHERE pid IN (715) and geosite_id=2;
UPDATE geothing SET country_code='SK', country_name='Slovakia', admin_code='08', oblast_name='Zilinsky Kraj' WHERE pid IN (1204) and geosite_id=2;
UPDATE geothing SET country_code='BY', country_name='Belarus', admin_code='05', oblast_name='Minskaya Voblasts\'' WHERE pid IN (11290) and geosite_id=1;
UPDATE geothing SET country_code='GE', country_name='Georgia', admin_code='02', oblast_name='Abkhazia' WHERE pid IN (11288, 11276) and geosite_id=1;
UPDATE geothing SET country_code='TJ', country_name='Tajikistan', admin_code='03', oblast_name='Viloyati Sughd' WHERE pid IN (11184) and geosite_id=1;
UPDATE geothing SET country_code='BY', country_name='Belarus', admin_code='02', oblast_name='Homyel\'skaya Voblasts\'' WHERE pid IN (11131) and geosite_id=1;


UPDATE geothing SET admin_code='777', oblast_name='undefined subject' WHERE country_code IS NOT NULL AND admin_code IS NULL;





