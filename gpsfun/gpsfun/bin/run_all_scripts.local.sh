touch /home/kostin/dev/www.GPS-FUN.INFO/cron_start.txt
/home/kostin/dev/www.GPS-FUN.INFO/gpsfun/bin/run.py /home/kostin/dev/www.GPS-FUN.INFO/gpsfun/scripts/update_geocacher_logs.py
/home/kostin/dev/www.GPS-FUN.INFO/gpsfun/bin/run.py /home/kostin/dev/www.GPS-FUN.INFO/gpsfun/scripts/calculate_cach_statistics.py
/home/kostin/dev/www.GPS-FUN.INFO/gpsfun/bin/run.py /home/kostin/dev/www.GPS-FUN.INFO/gpsfun/scripts/calculate_geocacher_statistics.py
/home/kostin/dev/www.GPS-FUN.INFO/gpsfun/bin/run.py /home/kostin/dev/www.GPS-FUN.INFO/gpsfun/scripts/calculate_geocacher_search_statistics.py
/home/kostin/dev/www.GPS-FUN.INFO/gpsfun/bin/run.py /home/kostin/dev/www.GPS-FUN.INFO/gpsfun/scripts/set_status_updated.py
touch /home/kostin/dev/www.GPS-FUN.INFO/cron_end.txt
