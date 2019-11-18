from isign_base_test import IsignBaseTest
from os import environ
import hashlib

PORT = 4744  # ISIG


class SigningServiceConfig(object):
    """ To be shared between the test Signing Service and client, so they both know where to find things """

    def __init__(self):
        self.host = 'localhost'
        self.port = PORT

        # overrides so you can test this with "real" keys and certs that we can't include in this library
        certificate = IsignBaseTest.CERTIFICATE
        if 'CERTIFICATE' in environ:
            certificate = environ['CERTIFICATE']

        key = IsignBaseTest.KEY
        if 'KEY' in environ:
            key = environ['KEY']

        with open(certificate, 'r') as fh:
            cert_sha1_hex = hashlib.sha1(fh.read()).hexdigest()

        # The signing server knows the contents of keys, and the client
        # invokes them with the related certificates's sha1 hash
        self.cert_hash_to_key_file = {
            cert_sha1_hex: key
        }
