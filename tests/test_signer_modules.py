from isign import isign
from isign_base_test import IsignBaseTest
import logging
from os.path import dirname, join, realpath
import sys


log = logging.getLogger(__name__)


class TestSignerModules(IsignBaseTest):

    def test_signer_class(self):

        lib_dir_path = join(dirname(realpath(__file__)), 'TestPythonLibDir')
        log.debug("library directory: {}".format(lib_dir_path))

        calls = []   # Py2 won't allow to refer to outer scope by assignment, e.g. isCalled = True
                     # To let the outer scope know a thing happened, must alter a mutable object - like an array!
        def callback(x):
            log.debug("The callback was fired")
            calls.append(x)

        output_path = self.get_temp_file()

        try:
            sys.path.append(lib_dir_path)
            print sys.path

            from FooSigner import FooSigner

            isign.resign(
                IsignBaseTest.TEST_IPA,

		certificate=IsignBaseTest.CERTIFICATE,
                provisioning_profile=IsignBaseTest.PROVISIONING_PROFILE,
                output_path=output_path,
                signer_class=FooSigner,
                signer_arguments={'callback': callback}
            )
            assert len(calls) > 0
        finally:
            sys.path.remove(lib_dir_path)
