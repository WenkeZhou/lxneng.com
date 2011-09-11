import os

from pyramid.view import view_config
from pyramid.response import Response


_here = os.path.dirname(__file__)
_robots = open(os.path.join(_here, '../static', 'robots.txt')).read()
_robots_response = Response(content_type='text/plain', body=_robots)
_favicon = open(os.path.join(_here, '../static', 'favicon.ico')).read()
_favicon_response = Response(content_type='image/x-icon', body=_favicon)


class BaseHandler(object):

    def __init__(self, request):
        self.request = request
        self.request.locale_name = request.params.get('lang', 'en')

    def __call__(self):
        return {}


@view_config(name='robots.txt')
def robotstxt_view(context, request):
    return _robots_response


@view_config(name='favicon.ico')
def favicon_view(context, request):
    return _favicon_response


@view_config(context='pyramid.exceptions.NotFound', renderer='404.html')
class Error(BaseHandler):
    pass


@view_config(route_name='home', renderer='home.html')
@view_config(route_name='about', renderer='home.html')
class Home(BaseHandler):
    pass
