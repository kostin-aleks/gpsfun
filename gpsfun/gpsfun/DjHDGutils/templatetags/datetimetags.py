from django.template import Library
from django.conf import settings
from django.utils.translation import ungettext, ugettext as _
from datetime import datetime

register = Library()

# NOTE: this functions is not localized (use settings.DATETIME_FORMAT)
@register.filter
def dt(value, arg=None):
    """Formats a date according to the given format."""
    from django.utils.dateformat import format
    if not value:
        return u''
    if arg is None:
        arg = settings.DATETIME_FORMAT
    return format(value, arg)
dt.is_safe = False

@register.filter
def date_diff(d):
    if d is None:
        return ''
    now = datetime.now()
    today = datetime(now.year, now.month, now.day)
    delta = now - d
    delta_midnight = today - d
    days = delta.days
    hours = round(delta.seconds / 3600., 0)
    minutes = round(delta.seconds / 60., 0)
    chunks = (
        (365.0, lambda n: ungettext('year', 'years', n)),
        (30.0, lambda n: ungettext('month', 'months', n)),
        (7.0, lambda n : ungettext('week', 'weeks', n)),
        (1.0, lambda n : ungettext('day', 'days', n)),
    )

    if days == 0:
        if hours == 0:
            if minutes > 0:
                return ungettext('1 minute ago', \
                    '%(minutes)d minutes ago', minutes) % \
                    {'minutes': minutes}
            else:
                return _("less than 1 minute ago")
        else:
            return ungettext('1 hour ago', '%(hours)d hours ago', hours) \
            % {'hours':hours}

    if delta_midnight.days == 0:
        return _("yesterday at %s") % d.strftime("%H:%M")

    count = 0
    for i, (chunk, name) in enumerate(chunks):
        if days >= chunk:
            count = round((delta_midnight.days + 1)/chunk, 0)
            break

    return _('%(number)d %(type)s ago') % \
        {'number': count, 'type': name(count)}



#do not use decorator here pls
def timedelta_format(delta):
    if delta.days < 0 or delta.seconds < 0:
        sign='-'
        sec = abs(delta.days)*24*60*60 - abs(delta.seconds)
    else:
        sec = abs(delta.days)*24*60*60 + abs(delta.seconds)
        sign=''
        
    min, sec = divmod(sec, 60)
    hrs, min = divmod(min, 60)
    return u'%s%02d:%02d:%02d' % (sign, hrs, min, sec) 


register.filter('timedelta_format', timedelta_format)
