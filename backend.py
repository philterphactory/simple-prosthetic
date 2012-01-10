import urllib
import logging

from google.appengine.ext.deferred.deferred import defer

import settings
import models
import prosthetic


def queue_run_weavr(name, _countdown=0):
    defer(do_run_weavr, name, _countdown=_countdown, _url='/defer/run_weavr/%s' % urllib.quote_plus(name))


def do_run_weavr(name):
    weavr = models.Weavr.get_by_key_name(name)
    if not weavr:
        logging.warning(u"Cannot run weavr %s, it doesn't exist" % name)
        return
    weavrs_instance = weavr.get_instance()
    if not weavrs_instance:
        logging.error(u"Cannot run weavr %s, cannot find WeavrsInstance" % name)
        return
    prosthetic.run(weavrs_instance, weavr)
