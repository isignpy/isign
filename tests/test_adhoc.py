from isign_base_test import IsignBaseTest
from isign import isign
import os
from os.path import exists
import logging

log = logging.getLogger(__name__)


class TestAdhoc(IsignBaseTest):

    def test_adhoc_signing(self):
        """
        Ad-hoc signing is "identityless" signing. We indicate this by simply not providing the key.

        These options were added by Facebook. It's not obvious if they still work.
        This test looks like it should work, but doesn't because other parts of the code still want an
        Entitlements file?
        """
        output_path = self.get_temp_file()
        isign.resign(self.TEST_IPA,
                     key=None,
                     provisioning_profile=IsignBaseTest.PROVISIONING_PROFILE,
                     output_path=output_path)
        assert exists(output_path)
        assert os.path.getsize(output_path) > 0
        self.unlink(output_path)
