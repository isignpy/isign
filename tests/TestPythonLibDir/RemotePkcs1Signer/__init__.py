import base64
import requests


class RemotePkcs1Signer(object):
    """ Client-side Signer subclass, that calls the Signing Service over HTTP to sign things """

    # payload should look like this, for the string 'foobar'.
    #
    # {"key": "demo-signing-with-haas", "plaintext": [{"key": "0", "value": "Zm9vYmFyCg=="}],
    #    "algorithm": "SIGNATURE_RSA_PKCS1_SHA256"}

    # Expected return:
    # {
    #     "signature": { "0": detached_signature_hex_string }
    # }

    # standard headers for request
    headers = {
        'Content-Type': 'application/json',
        'Accept': 'application/json'
    }

    def __init__(self, host, port, key, algorithm="SIGNATURE_RSA_PKCS1_SHA256", keyfile=None):
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
