from datetime import datetime
from django.conf import settings
from django.middleware import csrf

def uniq(str):
    """ convert str to unique value and return """
    return '%s%s' % (str, datetime.now().strftime('%Y%m%d%H%M%S'))


def uniqm(str=''):
    """ convert str to month-unique value and return """
    return '%s%s' % (str, datetime.now().strftime('%y%m'))

class TEST_USER:
    LOGIN = 'galdor'
    PASSWORD = 'GjhjKjyGjhjKjy'

def test_user_login(client):
    r = client.get('/login/')
    csrf_token = r._request.META['CSRF_COOKIE']
    r = client.post('/login/', {'username': TEST_USER.LOGIN,
                            'password': TEST_USER.PASSWORD,
                             'csrfmiddlewaretoken': csrf_token
                             }
                    )

def test_user_logout(client):
    client.post('/logout/')

