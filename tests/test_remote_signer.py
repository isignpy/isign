
from isign import isign
from isign_base_test import IsignBaseTest
import os
from signing_service_config import SigningServiceConfig
import subprocess
import sys
import time
from TestPythonLibDir.RemotePkcs1Signer import RemotePkcs1Signer


CONFIG = SigningServiceConfig()


class TestRemoteSigner(IsignBaseTest):

    @staticmethod
    def start_httpd():
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
            time.sleep(10)

            isign.resign(
                IsignBaseTest.TEST_IPA,
                certificate=IsignBaseTest.CERTIFICATE,
                provisioning_profiles=[IsignBaseTest.PROVISIONING_PROFILE],
                output_path=output_path,
                signer_class=RemotePkcs1Signer,
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
