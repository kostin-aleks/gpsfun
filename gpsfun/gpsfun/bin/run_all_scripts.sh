touch /var/www/htdocs/cron_start.txt
/var/www/htdocs/gpsfun/bin/run.py /var/www/htdocs/gpsfun/scripts/update_geocacher_logs.py
/var/www/htdocs/gpsfun/bin/run.py /var/www/htdocs/gpsfun/scripts/calculate_cach_statistics.py
/var/www/htdocs/gpsfun/bin/run.py /var/www/htdocs/gpsfun/scripts/calculate_geocacher_statistics.py
/var/www/htdocs/gpsfun/bin/run.py /var/www/htdocs/gpsfun/scripts/calculate_geocacher_search_statistics.py
/var/www/htdocs/gpsfun/bin/run.py /var/www/htdocs/gpsfun/scripts/set_status_updated.py
touch /var/www/htdocs/cron_end.txt
