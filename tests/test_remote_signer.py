from BaseHTTPServer import BaseHTTPRequestHandler, HTTPServer

import hashlib
from isign import isign
from isign_base_test import IsignBaseTest
import json

import logging
import requests

import cgi



log = logging.getLogger(__name__)



# Request format
# {
#    "key": certdata_sha1_hex_string,
#    "plaintext": { "0": unsigned_data_hex_string },
#    "algorithm": "SIGNATURE_RSA_RAW",
# }

config = [
    {
	key: IsignBaseTest.KEY,
	certificate: IsignBaseTest.CERTIFICATE
    }
]

signing_service_config = {}

with open(item['certificate'], "r") as fh:
    # NOTE: our test cert file is in PEM format.
    # If hashes are based on what Keychain does, it will be different.
    cert_sha1_hex = hashlib.sha1(fh.read()).hexdigest()
    signing_service_config[cert_sha1_hex] = item['key']

from BaseHTTPServer import BaseHTTPRequestHandler, HTTPServer
import SocketServer
import json
import cgi


class Server(BaseHTTPRequestHandler):
    def _set_headers(self):
	self.send_response(200)
	self.send_header('Content-type', 'application/json')
	self.end_headers()

    # POST echoes the message adding a JSON field
    def do_POST(self):
	ctype, pdict = cgi.parse_header(self.headers.getheader('content-type'))

	# refuse to receive non-json content
	if ctype != 'application/json':
	    self.send_response(400)
	    self.end_headers()
	    return

	# read the message and convert it into a python dictionary
	length = int(self.headers.getheader('content-length'))
	message = json.loads(self.rfile.read(length))

	# add a property to the object, just to mess with data
	message['received'] = 'ok'

	# send the message back
	self._set_headers()
	self.wfile.write(json.dumps(message))


def run(server_class=HTTPServer, handler_class=Server, port=8008):
    server_address = ('', port)
    httpd = server_class(server_address, handler_class)

    print 'Starting httpd on port %d...' % port
    httpd.serve_forever()

class RemoteSigningService(object):
    def do_POST(self, data):



# TODO: when Signer is just a naked signing algorithm, do that instead
# {
#     "signature": { "0": detached_signature_hex_string }
# }
class RemoteSigner(isign.Signer):
    def __init__(self):
	#
    def sign(self, data):
	requests.




class TestRemoteSigner(IsignBaseTest):

    def test_remote_signer(self):

	isign.resign(
	    IsignBaseTest.TEST_IPA,
	    provisioning_profile=IsignBaseTest.PROVISIONING_PROFILE,
	    output_path=output_path,
	    signer_class=RemoteSigner,
	    signer_arguments={
		'certificate': IsignBaseTest.CERTIFICATE,
		'apple_certificate': isign.isign.DEFAULT_APPLE_CERT_PATH
	    }
	)
