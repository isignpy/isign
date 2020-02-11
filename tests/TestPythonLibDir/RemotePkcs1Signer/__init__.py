import base64
import requests


class RemotePkcs1Signer(object):
    """ Client-side Signer subclass, that calls the Signing Service over HTTP to sign things """

    # standard headers for request
    headers = {
        'Content-Type': 'application/json',
        'Accept': 'application/json'
    }

    def __init__(self, host, port, key, algorithm="SIGNATURE_RSA_PKCS1_SHA256", keyfile=None):
	"""
	:param host:  host of the remote HTTP service
	:param port:  port of the remote HTTP service
	:param key:   see signing_service.py, in our case we use the hash of the related cert to identify the key
	:param algorithm: which algorithm to use
	:param keyfile: unused, this is a wart :(
	"""
        self.endpoint = "http://{}:{}/".format(host, port)
        self.key = key
        self.algorithm = algorithm

    def sign(self, data):
        plaintext_base64 = base64.b64encode(data)
        plaintext_key = u'0'
        payload = {
            "key": self.key,
            "plaintext": [{
                "key": plaintext_key,
                "value": plaintext_base64
            }],
            "algorithm": self.algorithm
        }

        response = requests.post(self.endpoint,
                                 headers=self.__class__.headers,
                                 json=payload).json()
        signature = base64.b64decode(response[u'signature'][plaintext_key])
        return signature
