UPDATE geothing gt
LEFT JOIN cach ON gt.pid = cach.pid
SET gt.country_code = cach.country_code,
gt.admin_code = cach.admin_code,
gt.country_name = cach.country_name,
gt.oblast_name = cach.oblast_name
WHERE cach.country_code IS NOT NULL;


UPDATE geothing gt
SET gt.admin_code = '777', 
gt.oblast_name = 'undefined subject'
WHERE gt.country_code IS NOT NULL AND
gt.admin_code IS NULL;
