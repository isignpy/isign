
from isign import isign
from isign_base_test import IsignBaseTest
from multiprocessing import Process
from signing_service import SigningService
from signing_service_config import SigningServiceConfig
import time
from TestPythonLibDir.RemotePkcs1Signer import RemotePkcs1Signer


CONFIG = SigningServiceConfig()


class TestRemoteSigner(IsignBaseTest):

    @staticmethod
    def start_httpd():
        signing_service = SigningService()

        def start():
            signing_service.start()

        httpd_process = Process(name='signing_service', target=start)
        httpd_process.daemon = True
        httpd_process.start()
        time.sleep(1)
        return httpd_process

    def test_remote_signer(self):

        output_path = self.get_temp_file()

        httpd_process = None

        try:
            httpd_process = self.start_httpd()

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
                httpd_process.terminate()
