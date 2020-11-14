from twisted.web import http
from twisted.python import log
import simplejson as json
import settings
import md5

def queryFailed(failure, request, message):
    if request:
        request.setResponseCode(http.INTERNAL_SERVER_ERROR)
        request.write(json.dumps({'status':'error','errors':[message % (failure.getErrorMessage())]}))
        request.finish()
    else:
        log.err(message % (failure.getErrorMessage()))

def make_random_job_key(length=10, allowed_chars='abcdefghjkmnpqrstuvwxyzABCDEFGHJKLMNPQRSTUVWXYZ23456789'):
    from random import choice
    return ''.join([choice(allowed_chars) for i in range(length)])

def sign(s):
    return md5.md5(s+settings.SECURE_KEY).hexdigest()

def check_correct_sign(s, signature):
    return sign(s)==signature
