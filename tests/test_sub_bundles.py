from isign_base_test import IsignBaseTest
import logging

log = logging.getLogger(__name__)


class TestSubBundles(IsignBaseTest):
    def test_matching_provisioning_profiles(self):
        """ TODO - Given an app with sub-bundles, test that provisioning profiles are matched to the correct bundles """
        # Get an app with sub-bundles, like the WatchKit app
        # In arguments to isign.resign, use multiple provisioning profiles which cannot be applied to all sub-bundles
        # Check that the app has the right pprofs in the right places
        # On MacOS, test that the app verifies correctly
        pass

    def test_matching_entitlements(self):
        """ TODO - Given an app with sub-bundles, test that entitlements are replaced in the correct bundles """
        # Get an app with sub-bundles, like the WatchKit app
        # In arguments to isign.resign, use multiple entitlements files
        # Check that entitlements are updated in the right places
        # On MacOS, check that the app verifies correctly
        pass