__version__ = '1.0.0'

from isign.signer import Pkcs1Signer
import logging

log = logging.getLogger(__name__)


class FooSigner(Pkcs1Signer):
    def __init__(self,
                 keyfile=None,
                 callback=None):
        super(FooSigner, self).__init__(keyfile)
        self.callback = callback

    def sign(self, data):
        log.info("I am FooSigning, with this callback...")
        log.info(self.callback)
        self.callback("FooSigner was here")
        return super(FooSigner, self).sign(data)