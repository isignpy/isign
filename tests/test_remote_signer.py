
import base64
from isign import isign
from isign_base_test import IsignBaseTest
import os
import pprint
from signing_service_config import SigningServiceConfig
import subprocess
import requests
import sys
import time


CONFIG = SigningServiceConfig()
pp = pprint.PrettyPrinter(indent=4)


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

    def __init__(self, host, port, key, algorithm="SIGNATURE_RSA_PKCS1_SHA256"):
	self.host = host
	self.port = port
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
	headers = {
	    'Content-Type': 'application/json',
	    'Accept': 'application/json'
	}
	url = "http://{}:{}/".format(CONFIG.host, CONFIG.port)

	response = requests.post(url, json=payload, headers=headers).json()
	signature = base64.b64decode(response[u'signature'][plaintext_key])
	return signature


class TestRemoteSigner(IsignBaseTest):

    def start_httpd(self):
	with open(os.devnull, 'w') as dev_null:
	    test_dir = os.path.dirname(os.path.abspath(__file__))
	    start_httpd_command = [sys.executable, os.path.join(test_dir, "signing_service.py")]
	    httpd_process = subprocess.Popen(start_httpd_command, stdout=dev_null, stderr=dev_null)
	    # wait for httpd to start. As far as I know this is the simplest thing to do, without:
	    #   - in the server, subclassing HTTPServer to print a message when ready (and even that's not reliable)
	    #   - starting a thread and blocking here to wait for it
	    time.sleep(1)
	    return httpd_process

    def test_remote_signer(self):
	output_path = self.get_temp_file()

	httpd_process = None

	try:
	    httpd_process = self.start_httpd()

	    isign.resign(
		IsignBaseTest.TEST_IPA,
		key=None,   # ugh this is so ugly, we should introduce defaults in command line processing,
			    # not later
		certificate=IsignBaseTest.CERTIFICATE,
		provisioning_profile=IsignBaseTest.PROVISIONING_PROFILE,
		output_path=output_path,
		signer_class=RemotePkcs1Signer,    # This is also ugly. Perhaps there should be a different interface
		signer_arguments={
		    'host': CONFIG.host,
		    'port': CONFIG.port,
		    'key': CONFIG.cert_hash_to_key_file.keys()[0]
		}
	    )
	    # test the output path for correctness
	finally:
	    if httpd_process is not None:
		httpd_process.kill()


