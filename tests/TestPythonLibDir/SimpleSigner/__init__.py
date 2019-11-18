__version__ = '1.0.0'

from isign.signer import Pkcs1Signer
import logging

log = logging.getLogger(__name__)


class SimpleSigner(Pkcs1Signer):
    """ A simple subclass of the standard signer. Good for testing the command-line invocation of a signer module,
        because it prints a message to stdout  """
    def __init__(self,
                 keyfile=None):
        super(SimpleSigner, self).__init__(keyfile)

    def sign(self, data):
        print("SimpleSigner was here")
        return super(SimpleSigner, self).sign(data)