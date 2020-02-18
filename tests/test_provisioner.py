from isign_base_test import IsignBaseTest
import logging

log = logging.getLogger(__name__)


class TestProvisioner(IsignBaseTest):
    def test_provisioning_profiles(self):
        """ TODO - Check that Provisioner returns the right provisioning profile for a bundle id """
        # Construct a Provisioner with multiple pprof files which are tied to different id-patterns
        # (We will need to make some fake pprofs for this!)
        # check that get_provisioning_profile returns the right one for each bundle id
        # test_identifier_matcher already does this exhaustively, just check basic functionality
        pass

    def test_entitlements(self):
        """ TODO - Check that Provisioner returns the right entitlements for a bundle id """
        # Same as above, but for entitlements files
        pass
