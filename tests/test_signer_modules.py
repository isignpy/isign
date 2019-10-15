from isign import isign
from isign_base_test import IsignBaseTest
import logging
from os.path import dirname, join, realpath
import sys


log = logging.getLogger(__name__)

class TestSignerModules(IsignBaseTest):

    is_called = False

    def callback(self):
        TestSignerModules.is_called = True

    def test_signer_module(self):

        lib_dir_path = join(dirname(realpath(__file__)), 'TestPythonLibDir')
        print lib_dir_path

        try:
            sys.path.append(lib_dir_path)
            print sys.path
            isign.resign(
                IsignBaseTest.TEST_IPA,
                signer_module='FooSigner.FooSigner',
                signer_module_arguments={'callback': TestSignerModules.callback})
            assert TestSignerModules.is_called
        finally:
            sys.path.remove(lib_dir_path)
