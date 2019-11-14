__version__ = '1.0.0'

import logging

log = logging.getLogger(__name__)


class FooSigner(object):
    def __init__(self,
                 keyfile=None,
                 callback=None):
        self.keyfile = keyfile
        self.callback = callback

    def sign(self, data):
        log.info("I am FooSigning, with this callback...")
        log.info(self.callback)
        self.callback("FooSigner was here")
        return ''