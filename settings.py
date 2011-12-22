import logging

import bottle

DEBUG = True
if DEBUG:
    LOG_LEVEL = logging.DEBUG
else:
    LOG_LEVEL = logging.WARNING

logging.basicConfig(level=LOG_LEVEL)
logging.root.setLevel(LOG_LEVEL)

if DEBUG:
    bottle.debug(True)
