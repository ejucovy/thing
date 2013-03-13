"""
WSGI config for thing project.

This module contains the WSGI application used by Django's development server
and any production WSGI deployments. It should expose a module-level variable
named ``application``. Django's ``runserver`` and ``runfcgi`` commands discover
this application via the ``WSGI_APPLICATION`` setting.

Usually you will have the standard Django WSGI application here, but it also
might make sense to replace the whole Django WSGI application with a custom one
that later delegates to the Django one. For example, you could introduce WSGI
middleware here, or combine a Django application with an application of another
framework.

"""
import os

# We defer to a DJANGO_SETTINGS_MODULE already in the environment. This breaks
# if running multiple sites in the same mod_wsgi process. To fix this, use
# mod_wsgi daemon mode with each site in its own daemon process, or use
# os.environ["DJANGO_SETTINGS_MODULE"] = "thing.settings"
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "thing.settings")

# This application object is used by any WSGI server configured to use this
# file. This includes Django's development server, if the WSGI_APPLICATION
# setting points here.
from django.core.wsgi import get_wsgi_application
django = get_wsgi_application()

from libopencore.http_proxy import RemoteProxy

#deliverance = get_deliverance_application()

from webob import Request, Response
import json

from libopencore.deliverance_middleware import filter_factory as Deliverance
from lxml.etree import fromstring
from deliverance.ruleset import RuleSet
from deliverance.middleware import FileRuleGetter

class TemplateRuleGetter(object):
    def __init__(self, rules, *args, **kw):
        self.rules = rules

    def __call__(self, get_resource, app, orig_req):
        return RuleSet.parse_xml(fromstring(self.rules), '')

deliverance = Deliverance({})

def middleware(environ, start_response):
    request = Request(environ.copy())
    response = request.get_response(django)

    if response.status_int != 305:
        return response(environ, start_response)
    data = json.loads(response.body)

    proxy = RemoteProxy([data['base_url']], rewrite_links=True)

    environ.pop("HTTP_ACCEPT_ENCODING", None)

    environ['SCRIPT_NAME'] = str(data['script_name']).rstrip("/")
    environ['PATH_INFO'] = "/" + str(data['path_info'].lstrip("/") )

    environ['HTTP_X_THING_THEME'] = data['theme']

    filter = deliverance(proxy)

    def per_project_theme(environ):
        return "%(wsgi.url_scheme)s://%(HTTP_HOST)s%(HTTP_X_THING_THEME)s" % environ
    filter.default_theme = per_project_theme
    filter.rule_getter = TemplateRuleGetter(data['deliverance_rules'])
    
    rq= Request(environ)
    resp = rq.get_response(filter)

    return resp(environ, start_response)
    
application = middleware
