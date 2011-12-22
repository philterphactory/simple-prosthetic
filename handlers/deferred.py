import logging

from google.appengine.ext import webapp
from google.appengine.ext.deferred import application as gae_deferred_application

import settings


def app(environ, start_response):
    old_level = logging.root.level
    logging.root.setLevel(settings.LOG_LEVEL)
    return gae_deferred_application(environ, start_response)
    logging.root.setLevel(old_level)
