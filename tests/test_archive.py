from isign_base_test import IsignBaseTest
from isign.archive import archive_factory, Archive, AppArchive, AppZipArchive, IpaArchive
import logging

log = logging.getLogger(__name__)


class TestArchive(IsignBaseTest):

    def _test_good(self, filename, klass):
        archive = archive_factory(filename)
        assert archive is not None
        assert archive.__class__ is klass
        assert isinstance(archive, Archive)

    def test_archive_factory_app(self):
        self._test_good(self.TEST_APP_XCODE7, AppArchive)

    def test_archive_factory_appzip(self):
        self._test_good(self.TEST_APPZIP_XCODE7, AppZipArchive)

    def test_archive_factory_ipa(self):
        self._test_good(self.TEST_IPA_XCODE7, IpaArchive)

    def test_archive_factory_nonapp_dir(self):
        archive = archive_factory(self.TEST_NONAPP_DIR)
        assert archive is None

    def test_archive_factory_nonapp_ipa(self):
        archive = archive_factory(self.TEST_NONAPP_IPA)
        assert archive is None

    def test_archive_factory_nonapp_txt(self):
        archive = archive_factory(self.TEST_NONAPP_TXT)
        assert archive is None

    def test_archive_factory_simulator_app(self):
        self._test_good(self.TEST_SIMULATOR_APP_XCODE7, AppZipArchive)


class TestBundleInfo(IsignBaseTest):

    def _test_bundle_info(self, filename):
        archive = archive_factory(filename)
        assert archive is not None
        assert archive.bundle_info is not None
        assert archive.bundle_info['CFBundleName'] in ['IsignTestApp', 'isignTestApp']

    def test_app_archive_info(self):
        self._test_bundle_info(self.TEST_APP_XCODE7)

    def test_appzip_archive_info(self):
        self._test_bundle_info(self.TEST_APPZIP_XCODE7)

    def test_ipa_archive_info(self):
        self._test_bundle_info(self.TEST_IPA_XCODE7)


class TestArchivePrecheck(IsignBaseTest):

    def test_precheck_app(self):
        assert AppArchive.precheck(self.TEST_APP_XCODE7)

    def test_precheck_appzip(self):
        assert AppZipArchive.precheck(self.TEST_APPZIP_XCODE7)

    def test_precheck_ipa(self):
        assert IpaArchive.precheck(self.TEST_IPA_XCODE7)

    def test_bad_precheck_app(self):
        assert AppArchive.precheck(self.TEST_NONAPP_DIR) is False
        assert AppArchive.precheck(self.TEST_APPZIP_XCODE7) is False
        assert AppArchive.precheck(self.TEST_IPA_XCODE7) is False

    def test_bad_precheck_appzip(self):
        assert AppZipArchive.precheck(self.TEST_APP_XCODE7) is False
        assert AppZipArchive.precheck(self.TEST_IPA_XCODE7) is False

    def test_bad_precheck_ipa(self):
        assert IpaArchive.precheck(self.TEST_APP_XCODE7) is False
        assert IpaArchive.precheck(self.TEST_APPZIP_XCODE7) is False
        assert IpaArchive.precheck(self.TEST_NONAPP_IPA) is False
