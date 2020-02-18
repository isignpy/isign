from isign_base_test import IsignBaseTest
from isign import isign
import os
from os.path import exists
import logging

log = logging.getLogger(__name__)


class TestAdhoc(IsignBaseTest):

    def test_adhoc_signing(self):
        """
        Ad-hoc signing is "identityless" signing.
        """
        output_path = self.get_temp_file()
        isign.resign_adhoc(self.TEST_IPA_XCODE7,
                           output_path=output_path)
        assert exists(output_path)
        assert os.path.getsize(output_path) > 0
        self.unlink(output_path)
