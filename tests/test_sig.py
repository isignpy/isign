import isign
from isign_base_test import IsignBaseTest
from os.path import join


class TestCmsSigner(IsignBaseTest):

    def test_bad_signature(self):
        """ make openssl appear to return a bad signature """
        old_openssl = isign.openssl_shell.OPENSSL
        try:
            signer = isign.signer.CmsSigner(
                signer=isign.signer.Pkcs1Signer(self.KEY),
                signer_cert_file=self.CERTIFICATE,
                apple_cert_file=isign.isign.DEFAULT_APPLE_CERT_PATH)
            isign.signer.OPENSSL = join(self.TEST_DIR, "bad_openssl")
            with self.assertRaises(Exception):
                signer.sign("some data")
        finally:
            isign.openssl_shell.OPENSSL = old_openssl
