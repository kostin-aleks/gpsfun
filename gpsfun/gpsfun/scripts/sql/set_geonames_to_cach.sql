update cach left join geo_country on cach.country_code = geo_country.iso
set cach.country_name=geo_country.name 
where geo_country.name is not null;

update cach left join geo_country_subject gcs on cach.country_code = gcs.country_iso and cach.admin_code=gcs.code
set cach.oblast_name=gcs.name 
where gcs.name is not null;

