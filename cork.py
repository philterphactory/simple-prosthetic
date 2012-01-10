# the little things that makes the bottle more usable...

from bottle import request, response


SUCCESS = 'success'
WARNING = 'warning'
ERROR = 'error'


def get_flash():
    level, message = request.get_cookie('flash', secret='sekrit', default=(None,None))
    response.delete_cookie('flash', path='/')
    return level, message


def set_flash(level, message):
    response.set_cookie('flash', (level, message), secret='sekrit', path='/')


def stripslashes(v):
    if not v:
        return v
    assert isinstance(v, basestring)
    while v.startswith('/'):
        v = v[1:]
    while v.endswith('/'):
        v = v[:-1]
    return v
