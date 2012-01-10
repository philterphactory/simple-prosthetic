import logging
import weavrsclient

def run(weavrs_instance, weavr):
    """Do the prosthetic activity for a given weavr."""
    logging.info(u"Hello, weavr %s" % weavr.key().name())
    client = weavrsclient.WeavrsClient(weavrs_instance, weavr)
    config = client.get_weavr_configuration()
    logging.info(u"Got configuration: %s" % config)
