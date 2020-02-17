from isign import isign
from isign_base_test import IsignBaseTest
import logging
from TestPythonLibDir.CallbackSigner import CallbackSigner

log = logging.getLogger(__name__)


class TestSignerModules(IsignBaseTest):

    def test_signer_class(self):
        calls = []  # Py2 won't allow to refer to outer scope by assignment, e.g. isCalled = True

        # To let the outer scope know a thing happened, must alter a mutable object - like an array!
        def callback(x):
            log.debug("The callback was fired")
            calls.append(x)

        output_path = self.get_temp_file()

        isign.resign(
            IsignBaseTest.TEST_IPA,
            key=None,
            certificate=IsignBaseTest.CERTIFICATE,
            provisioning_profiles=[IsignBaseTest.PROVISIONING_PROFILE],
            output_path=output_path,
            signer_class=CallbackSigner,
            signer_arguments={'callback': callback, 'keyfile': IsignBaseTest.KEY}
        )
        assert len(calls) > 0
