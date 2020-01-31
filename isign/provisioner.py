""" Provides access to provisioning profiles and entitlements that could be
    useful while signing. """

import biplist
from exceptions import BadIdentifier
import logging
from openssl_shell import OpenSslShell

log = logging.getLogger(__name__)


class IdentifierMatcher(object):
    """
       iOS apps use different kinds of identifiers (bundle ids, application ids, etc) usually in the form
       of TEAMID.tld.domain.myapp.myotherthing and sometimes with wildcards at the end like TEAMID.* .

       It is sometimes important to know if one id encompasses another. For instance, if you have a provisioning
       profile whose "application-identifier" covers TEAMID.foo.bar.*, and you have a bundle whose CFBundleIdentifier
       is TEAMID.foo.bar.baz. Is that provisioning profile good? In this case yes.

       This class also helps us decide which of many options is the most specific fit

       Because id is so overloaded here, the id we are trying to "fit" into is called the pattern, even if it's just
       another id.
    """
    @classmethod
    def get_best_pattern(cls, identifier, patterns):
        """ Return the best pattern that matched this identifier. May return None """
        best_pattern = None
        patterns_scored = [(pattern, cls.get_score(identifier, pattern)) for pattern in patterns]
        patterns_matching = filter(lambda tup: tup[1] > 0, patterns_scored)
        if len(patterns_matching) > 0:
            (best_pattern, _) = sorted(patterns_matching, key=lambda tup: tup[1])[-1]
        return best_pattern

    @classmethod
    def get_score(cls, identifier, pattern):
        """ Given an identifier like
                TEAMID.tld.domain.myapp

            and a pattern which is either a wildcard or fully-qualified, like:
                TEAMID.*
                TEAMID.tld.domain.myapp
                TEAMID.tld.domain.myapp.*
                TEAMID.tld.domain.myapp.mywatchkitapp

            return an natural number score of how well the pattern matches the id.
            0 means no match at all
        """
        score = 0
        if identifier is None or identifier is '':
            raise BadIdentifier("id doesn't look right: {}".format(identifier))
        if pattern is None or pattern is '':
            raise BadIdentifier("pattern doesn't look right: {}".format(pattern))

        identifier_parts = identifier.split('.')
        pattern_parts = pattern.split('.')
        try:
            star_index = pattern_parts.index('*')
            if star_index != -1 and star_index != len(pattern_parts) - 1:
                raise BadIdentifier("pattern has a non-terminal asterisk: {}".format(pattern))
        except ValueError:
            pass

        # to be a match, there must be equal or fewer pattern parts. Neither 'foo.bar' nor 'foo.*' can match 'foo'
        i = 0
        p = 0
        while i < len(identifier_parts) or p < len(pattern_parts):
            if p < len(pattern_parts) and i < len(identifier_parts):
                if identifier_parts[i] == pattern_parts[p]:
                    i = i + 1
                    p = p + 1
                    score = score + 1
                    continue
                elif pattern_parts[p] == '*':
                    break
            score = 0
            break

        return score


class Provisioner(object):
    @classmethod
    def extract_entitlements(cls, provisioning_profile_path):
        log.debug("EXTRACTING ENTITLEMENTS")
        """ Given a path to a provisioning profile, return the entitlements
            encoded therein """
        cmd = [
            'smime',
            '-inform', 'der',
            '-verify',  # verifies content, prints verification status to STDERR,
            #  outputs content to STDOUT. In our case, will be an XML plist
            '-noverify',  # accept self-signed certs. Not the opposite of -verify!
            '-in', provisioning_profile_path
        ]
        # this command always prints 'Verification successful' to stderr.
        (profile_text, err) = OpenSslShell.command(cmd, data=None, expect_err=True)
        if err and err.strip() != 'Verification successful':
            log.error('Received unexpected error from openssl: {}'.format(err))
        plist_dict = biplist.readPlistFromString(profile_text)
        if 'Entitlements' not in plist_dict:
            log.debug('failed to get entitlements in provisioning profile')
            raise Exception('could not find Entitlements in {}'.format(provisioning_profile_path))
        return plist_dict['Entitlements']

    def __init__(self, provisioning_profile_paths, entitlements_paths):
        self.app_id_to_pprof_info = self.parse_provisioning_profiles(provisioning_profile_paths)
        # each provisioning profile should already have entitlements. But maybe you want to override them.
        # Note, it appears that overriden entitlements paths can only be "less" than the ones in the provisioning
        # profile. For instance, a property that in the provisioning profile is "foo.*" can be "foo.bar.baz" in the
        # entitlements, but not the reverse. We could do a sanity check here for that!
        self.app_id_to_entitlements = self.parse_entitlements(entitlements_paths)

    @staticmethod
    def parse_provisioning_profiles(cls, provisioning_profile_paths):
        """
        Parse provisioning profiles into a map of
            application id -> provisioning_profile path, entitlements as string
        """
        app_id_info = {}
        for provisioning_profile_path in provisioning_profile_paths:
            entitlements = cls.extract_entitlements(provisioning_profile_path)
            if 'application-identifier' not in entitlements:
                raise Exception("Could not find application-identifier in entitlements from provisioning profile {}"
                                .format(provisioning_profile_path))
            app_id = entitlements['application-identifier']
            if app_id in app_id_info:
                raise Exception("At least 2 provisioning profiles target the same application identifier: "
                                "{}, {}".format(provisioning_profile_path, app_id_info[app_id]))
            app_id_info[app_id] = {
                "provisioning_profile_path": provisioning_profile_path,
                "entitlements": biplist.writePlistToString(entitlements)
            }
        return app_id_info

    @classmethod
    def parse_entitlements(cls, entitlements_paths):
        """
           Parse additional entitlements files into a map of
             application id -> entitlements as a string
        """
        app_id_to_entitlements = {}
        for entitlements_path in entitlements_paths:
            entitlements = biplist.readPlist(entitlements_path)
            app_id = entitlements['application-identifier']
            if app_id in app_id_to_entitlements:
                raise Exception("At least 2 entitlements files target the same application identifier: "
                                "{}, {}".format(entitlements_path, app_id_to_entitlements[app_id]))
            app_id_to_entitlements[app_id] = biplist.readPlist(entitlements_path)
        return app_id_to_entitlements

    def get_provisioning_profile(self, bundle_id):
        """ Return the path to the best provisioning profile for this identifier """
        pass

    def get_entitlements(self, bundle_id):
        """ Return the path to the best entitlements for this identifier """
        pass

