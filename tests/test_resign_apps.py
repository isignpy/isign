from isign_base_test import IsignBaseTest
import os
from os.path import exists
from isign import isign
import logging

log = logging.getLogger(__name__)


class TestResignApps(IsignBaseTest):

    def _test_signable(self, filename, output_path):
        self.resign(filename, output_path=output_path)
        assert exists(output_path)
        assert os.path.getsize(output_path) > 0
        self.unlink(output_path)

    def _test_unsignable(self, filename, output_path):
        with self.assertRaises(isign.NotSignable):
            self.resign(filename, output_path=output_path)
        self.unlink(output_path)

    def test_app_xcode7(self):
        self._test_signable(self.TEST_APP_XCODE7, self.get_temp_dir())

    def test_app_ipa_xcode7(self):
        self._test_signable(self.TEST_IPA_XCODE7, self.get_temp_file())

    def test_app_with_frameworks_ipa_xcode7(self):
        self._test_signable(self.TEST_WITH_FRAMEWORKS_IPA_XCODE7, self.get_temp_file())

    def test_appzip_xcode7(self):
        self._test_signable(self.TEST_APPZIP_XCODE7, self.get_temp_file())

    def test_non_app_txt(self):
        self._test_unsignable(self.TEST_NONAPP_TXT, self.get_temp_file())

    def test_non_app_ipa(self):
        self._test_unsignable(self.TEST_NONAPP_IPA, self.get_temp_file())

    def test_simulator_app_xcode7(self):
        self.resign_adhoc(self.TEST_SIMULATOR_APP_XCODE7, output_path=self.get_temp_file())

    def test_ipa_xcode11(self):
        self._test_signable(self.TEST_IPA_XCODE11, self.get_temp_file())

    def test_ipa_frameworks_ipa_xcode11(self):
        self._test_signable(self.TEST_FRAMEWORKS_IPA_XCODE11, self.get_temp_file())

    def test_watch_ipa_xcode11(self):
        self._test_signable(self.TEST_WATCH_IPA_XCODE11, self.get_temp_file())

