update geocacher
set created_caches = (
    select COUNT(l.id)
    from log_create_cach l
    where l.author_pid=geocacher.pid
    );

update geocacher
set found_caches = (
    select COUNT(l.id)
    from log_seek_cach l
    where l.cacher_pid=geocacher.pid
    );



