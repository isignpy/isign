""" Provides access to provisioning profiles and entitlements that could be
    useful while signing. """

import biplist
from exceptions import BadIdentifier
import logging
from openssl_shell import OpenSslShell

log = logging.getLogger(__name__)


class IdMatcher(object):
    @classmethod
    def get_best_wildcard(cls, identifier, wildcards):
        wildcard_scores = [(wildcard, cls.get_score(identifier, wildcard)) for wildcard in wildcards]
        (best_wildcard, _) = sorted(wildcard_scores, key=lambda tup: tup[1])
        return best_wildcard

    @classmethod
    def get_score(cls, identifier, wildcard):
        """ Given a string id like
                TEAMID.tld.domain.myapp

            and a string which is either wildcard or fully-qualified, like:
                TEAMID.*
                TEAMID.tld.domain.myapp
                TEAMID.tld.domain.myapp.*
                TEAMID.tld.domain.myapp.mywatchkitapp

            return an natural number score of how well the wildcard matches the id.
            0 means no match at all
        """
        score = 0
        if identifier is None or identifier is '':
            raise BadIdentifier("id doesn't look right: {}".format(identifier))
        if wildcard is None or wildcard is '':
            raise BadIdentifier("wildcard doesn't look right: {}".format(wildcard))

        id_parts = identifier.split('.')
        wildcard_parts = wildcard.split('.')

        # to be a match, there must be equal or fewer wildcard parts. Neither 'foo.bar' nor 'foo.*' can match 'foo'
        if len(wildcard_parts) <= len(id_parts):
            # iterate through wildcard parts and see if the all match their counterpart in id.
            i = 0
            while i < len(wildcard_parts):
                if wildcard_parts[i] == '*':
                    # star must be terminal
                    if i == len(wildcard_parts) - 1:
                        break
                    else:
                        raise Exception("wildcard looks wrong: {}".format(wildcard))

                if id_parts[i] == wildcard_parts[i]:
                    # the components are a match so far, keep going
                    score = score + 1
                    i = i + 1
                else:
                    # the components do not match - e.g. a.b.c.d and a.x.y, so fail!
                    score = 0
                    break

        return score


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
            raise Exception('could not find Entitlements in {}'.format(provision_path))
        return plist_dict['Entitlements']

    def __init__(self, provisioning_profile_paths, entitlements_paths):
        (app_id_to_pprof_path, app_id_to_entitlements_path) = self.parse_provisioning_profiles(provisioning_profile_paths)
        self.app_id_to_pprof_path = app_id_to_pprof_path
        self.app_id_to_entitlements_path = app_id_to_entitlements_path
        # each provisioning profile should already have entitlements. But maybe you want to override them.
        # Note, it appears that overriden entitlements paths can only be "less" than the ones in the provisioning
        # profile. For instance, a property that in the provisioning profile is "foo.*" can be "foo.bar.baz" in the
        # entitlements, but not the reverse. TODO We could do a sanity check here for that.
        self.app_id_to_entitlements_path.update(self.parse_entitlements(entitlements_paths))

    @staticmethod
    def parse_provisioning_profiles(cls, provisioning_profile_paths):
        app_id_to_pprof_path = {}
        app_id_to_entitlements_path = {}
        for provisioning_profile_path in provisioning_profile_paths:
            entitlements = self.extract_entitlements(provisioning_profile_path)
            if 'application-identifier' not in entitlements:
                raise Exception("Could not find application-identifier in entitlements from provisioning profile {}".format(provisioning_profile))
            app_id = entitlements['application-identifier']
            if app_id in app_id_to_pprof_path:
                raise Exception("At least 2 provisioning profiles target the same application identifier: "
                                "{}, {}".format(provisioning_profile_path, app_id_to_pprof_path[app_id]))
            app_id_to_pprof_path[app_id] = provisioning_profile_path
        # extract the pprof entitlements as paths (it's just convenient for later when we sign)
        entitlements_path = ... some temp file? 'Entitlements.plist'
        biplist.writePlist(entitlements, entitlements_path, binary=False)
        return (app_id_to_pprof_path, app_id_to_entitlements_path)

    @classmethod
    def parse_entitlements(cls, entitlements_paths):
        app_id_to_entitlements_path = {}
        for entitlements_path in entitlements_paths:
            entitlements = biplist.readPlist(entitlements_path)
            app_id = entitlements['application-identifier']
            if app_id in app_id_to_entitlements_path:
                raise Exception("At least 2 entitlements files target the same application identifier: "
                                "{}, {}".format(entitlements_path, app_id_to_pprof_path[app_id]))
            app_id_to_entitlements_path[app_id] = entitlements_path
        return app_id_to_entitlements_path

    def get_provisioning_profile(self, bundle_id):
        """ Return the path to the best provisioning profile for this bundle """
        pass

    def get_entitlements(self, bundle_id):
        """ Return the path to the best entitlements for this bundle """
        pass

