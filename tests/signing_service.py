import base64
from BaseHTTPServer import BaseHTTPRequestHandler, HTTPServer
import cgi
from isign.signer import Pkcs1Signer
import json
import os
import pprint
from signing_service_config import SigningServiceConfig
import sys

pp = pprint.PrettyPrinter(indent=4)
CONFIG = SigningServiceConfig()

# map the configured key files to signers, indexed by related certificate hash
cert_hash_to_signer = {cert_hash: Pkcs1Signer(key_file)
                       for cert_hash, key_file
                       in CONFIG.cert_hash_to_key_file.iteritems()}


class SigningServiceHandler(BaseHTTPRequestHandler):
    """ accepts POST requests with JSON bodies, to sign plaintext:
    {
        "key": "alias_for_private_key",
        "plaintext": [
            {
            "key": "0",
            "value": "Zm9vYmFyCg=="   # base64 encoded value
            "algorithm": "SIGNATURE_RSA_PKCS1_SHA256"
            }
        ]
        }

    The alias for the private key that we're using is the sha1 hash of the related certificate

    returns JSON in response:

        {
        "signature": { "0": base64_encoded_signature }
        }
    """

    # Class "variable" because we want to sometimes suppress logging, and the handler is only passed as
    # an uninitialized class reference. Ugly but this is just for tests
    quiet = False

    def _set_headers(self):
        self.send_response(200)
        self.send_header('Content-type', 'application/json')
        self.end_headers()

    def _client_error(self, message):
        self.send_response(400, message)
        self.end_headers()

    def do_GET(self):
        self._set_headers()
        self.wfile.write(json.dumps({"hi": "there"}))

    def do_POST(self):
        content_type, content_type_parts = cgi.parse_header(self.headers.getheader('content-type'))

        # refuse to receive non-json content
        if content_type != 'application/json':
            return self._client_error("Only send JSON plz")

        # read the message and convert it into a python dictionary
        length = int(self.headers.getheader('content-length'))
        message = json.loads(self.rfile.read(length))

        if not message['key'] in cert_hash_to_signer:
            return self._client_error("Don't recognize that key")

        pkcs1_signer = cert_hash_to_signer[message['key']]

        plaintexts = message['plaintext']
        signatures = {}
        for plaintext in plaintexts:
            plaintext_key = plaintext['key']
            plaintext_value = base64.b64decode(plaintext['value'])
            signature = pkcs1_signer.sign(plaintext_value)
            signatures[plaintext_key] = base64.b64encode(signature)

        signature_structure = {"signature": signatures}
        body = json.dumps(signature_structure)

        self._set_headers()
        self.wfile.write(body)

    def log_message(self, format, *args):
        if not self.quiet:
            BaseHTTPRequestHandler.log_message(self, format, *args)


class SigningService(object):
    """ Server-side signer """

    @staticmethod
    def start(quiet=False):
        SigningServiceHandler.quiet = quiet
        if not quiet:
            print('Starting httpd at {}:{}...'.format(CONFIG.host, CONFIG.port))
        httpd = HTTPServer((CONFIG.host, CONFIG.port), SigningServiceHandler)
        httpd.serve_forever()


if __name__ == '__main__':
    SigningService().start()
