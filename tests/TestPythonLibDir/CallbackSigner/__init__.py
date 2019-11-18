__version__ = '1.0.0'

from isign.signer import Pkcs1Signer
import logging

log = logging.getLogger(__name__)


class CallbackSigner(Pkcs1Signer):
    """ Simple subclass of the standard signer, which also accepts a callback. An automated
        test can then check that this signer successfully ran by seeing if that callback was called.
    """
    def __init__(self,
                 keyfile=None,
                 callback=None):
        super(CallbackSigner, self).__init__(keyfile)
        self.callback = callback

    def sign(self, data):
        log.info("I am CallbackSigner, calling this callback...")
        log.info(self.callback)
        self.callback("CallbackSigner was here")
        return super(CallbackSigner, self).sign(data)