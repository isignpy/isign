""" Provides access to provisioning profiles and entitlements that could be
    useful while signing. """

import biplist
from identifier_matcher import IdentifierMatcher
import logging
from openssl_shell import OpenSslShell

log = logging.getLogger(__name__)


class Provisioner(object):
    @classmethod
    def extract_entitlements(cls, provisioning_profile):
        log.debug("EXTRACTING ENTITLEMENTS")
        """ Given a path to a provisioning profile, return the entitlements
            encoded therein """
        cmd = [
            'smime',
            '-inform', 'der',
            '-verify',  # verifies content, prints verification status to STDERR,
            #  outputs content to STDOUT. In our case, will be an XML plist
            '-noverify',  # accept self-signed certs. Not the opposite of -verify!
            '-in', provisioning_profile
        ]
        # this command always prints 'Verification successful' to stderr.
        (profile_text, err) = OpenSslShell.command(cmd, data=None, expect_err=True)
        if err and err.strip() != 'Verification successful':
            log.error('Received unexpected error from openssl: {}'.format(err))
        plist_dict = biplist.readPlistFromString(profile_text)
        if 'Entitlements' not in plist_dict:
            log.debug('failed to get entitlements in provisioning profile')
            raise Exception('could not find Entitlements in {}'.format(provisioning_profile))
        return plist_dict['Entitlements']

    @classmethod
    def parse_provisioning_profiles(cls, provisioning_profiles):
        """
        Parse provisioning profiles into two maps of
            application id -> provisioning profile path
            application id -> dict of entitlements as string, provisioning profile path
        """
        app_id_to_pprof = {}
        app_id_to_entitlements_info = {}
        for provisioning_profile in provisioning_profiles:
            entitlements = cls.extract_entitlements(provisioning_profile)
            if 'application-identifier' not in entitlements:
                raise Exception("Could not find application-identifier in entitlements from provisioning profile {}"
                                .format(provisioning_profile))
            app_id = entitlements['application-identifier']
            if app_id in app_id_to_pprof:
                raise Exception("At least 2 provisioning profiles target the same application identifier: "
                                "{}, {}".format(provisioning_profile, app_id_to_pprof[app_id]))
            app_id_to_pprof[app_id] = provisioning_profile
            app_id_to_entitlements_info[app_id] = {
                "path": provisioning_profile,
                "entitlements": biplist.writePlistToString(entitlements)
            }
        return app_id_to_pprof, app_id_to_entitlements_info

    @classmethod
    def parse_entitlements(cls, entitlements_paths):
        """
           Parse additional entitlements files into a map of
             application id -> entitlements as a string
        """
        app_id_to_entitlements_info = {}
        for entitlements_path in entitlements_paths:
            entitlements = biplist.readPlist(entitlements_path)
            app_id = entitlements['application-identifier']
            if app_id in app_id_to_entitlements_info:
                raise Exception("At least 2 entitlements files target the same application identifier: "
                                "{}, {}".format(entitlements_path, app_id_to_entitlements_info[app_id]['source']))
            app_id_to_entitlements_info[app_id] = {
                "path": entitlements_path,
                "entitlements": biplist.readPlist(entitlements_path)
            }
        return app_id_to_entitlements_info

    def __init__(self, provisioning_profiles, entitlements_paths):
        log.debug("provisioner")
        log.debug(provisioning_profiles)
        log.debug(entitlements_paths)
        (app_id_to_pprof, app_id_to_entitlements_info) = self.parse_provisioning_profiles(provisioning_profiles)
        self.app_id_to_pprof = app_id_to_pprof
        log.debug(app_id_to_pprof)
        self.app_id_to_entitlements_info = app_id_to_entitlements_info
        log.debug(self.app_id_to_entitlements_info)

        # each provisioning profile should already have entitlements. But maybe you want to override them.
        self.app_id_to_entitlements_info.update(self.parse_entitlements(entitlements_paths))
        # Note, it appears that overriden entitlements paths can only be "less" than the ones in the provisioning
        # profile. For instance, a property that in the provisioning profile is "foo.*" can be "foo.bar.baz" in the
        # entitlements, but not the reverse. We could do a sanity check here for that!
        log.debug(self.app_id_to_entitlements_info)


    def get_provisioning_profile(self, identifier):
        """ Return the path to the best provisioning profile for this identifier """
        best_app_id = IdentifierMatcher.get_best_pattern(identifier, self.app_id_to_pprof.keys())
        if best_app_id is None:
            raise Exception("Cannot find provisioning profile for {}".format(identifier))
        provisioning_profile = self.app_id_to_pprof[best_app_id]
        log.debug("For team+bundle {}, using provisioning profile {}".format(identifier, provisioning_profile))
        return provisioning_profile

    def get_entitlements(self, identifier):
        """ Return the best entitlements for this identifier """
        best_app_id = IdentifierMatcher.get_best_pattern(identifier, self.app_id_to_entitlements_info.keys())
        if best_app_id is None:
            raise Exception("Cannot find entitlements for {}".format(identifier))
        entitlements_info = self.app_id_to_entitlements_info[best_app_id]
        log.debug("For team+bundle {}, using entitlements from {}".format(identifier, entitlements_info["path"]))
        return entitlements_info["entitlements"]

