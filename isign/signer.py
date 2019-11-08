#
# Small object that can be passed around easily, that represents
# our signing credentials, and can sign data.
#
# Unfortunately the installed python OpenSSL library doesn't
# offer what we need for cms, so we also need to shell out to the openssl
# tool, and make sure it's the right version.

from distutils import spawn
from exceptions import (ImproperCredentials,
                        MissingCredentials,
                        OpenSslFailure)
import logging
from OpenSSL import crypto
import os
import os.path
import subprocess
import re
import asn1crypto.cms
import binascii
import hashlib
from datetime import datetime

OPENSSL = os.getenv('OPENSSL', spawn.find_executable('openssl', os.getenv('PATH', '')))
# modern OpenSSL versions look like '0.9.8zd'. Use a regex to parse
OPENSSL_VERSION_RE = re.compile(r'(\d+).(\d+).(\d+)(\w*)')
MINIMUM_OPENSSL_VERSION = '1.0.1'

log = logging.getLogger(__name__)


def openssl_command(args, data=None, expect_err=False):
    """ Given array of args, and optionally data to write,
        return results of openssl command.
        Some commands always write something to stderr, so allow
        for that with the expect_err param. """
    cmd = [OPENSSL] + args
    cmd_str = ' '.join(cmd)
    # log.debug('running command ' + cmd_str)
    proc = subprocess.Popen(cmd,
                            stdin=subprocess.PIPE,
                            stderr=subprocess.PIPE,
                            stdout=subprocess.PIPE)
    if data is not None:
        proc.stdin.write(data)
    out, err = proc.communicate()

    if not expect_err:
        if err is not None and err != '':
            log.error("Command `{0}` returned error:\n{1}".format(cmd_str, err))

    if proc.returncode != 0:
        msg = "openssl command `{0}` failed, see log for error".format(cmd_str)
        raise OpenSslFailure(msg)

    if expect_err:
        return (out, err)
    else:
        return out


def get_installed_openssl_version():
    version_line = openssl_command(['version'])
    # e.g. 'OpenSSL 0.9.8zd 8 Jan 2015'
    return re.split(r'\s+', version_line)[1]


def is_openssl_version_ok(version, minimum):
    """ check that the openssl tool is at least a certain version """
    version_tuple = openssl_version_to_tuple(version)
    minimum_tuple = openssl_version_to_tuple(minimum)
    return version_tuple >= minimum_tuple


def openssl_version_to_tuple(s):
    """ OpenSSL uses its own versioning scheme, so we convert to tuple,
        for easier comparison """
    search = re.search(OPENSSL_VERSION_RE, s)
    if search is not None:
        return search.groups()
    return ()


class Pkcs1Signer(object):
    """ low-level PKCS#1 signer, which can be used by a CmsSigner to do
    the underlying signing operation """

    def __init__(self, keyfile):
        self.keyfile = keyfile
        pass

    def sign(self, data, password=""):
        key = open(self.keyfile, "r").read()
        pkey = crypto.load_privatekey(crypto.FILETYPE_PEM, key, password)

        return crypto.sign(pkey, data, "sha256")


class CmsSigner(object):
    """ collaborator, holds the keys, identifiers for signer,
        and knows how to sign data """
    def __init__(self,
		 signer,
                 signer_key_file=None,
                 signer_cert_file=None,
                 apple_cert_file=None,
                 team_id=None):
	""" signer: an initialized Signer module
	    signer_key_file = your org's key .pem  <--- TODO, eliminate
            signer_cert_file = your org's cert .pem
            apple_cert_file = apple certs in .pem form
            team_id = your Apple Organizational Unit code """

	log.debug('Signing with signer: {}'.format(signer.__class__.__name__))
        log.debug('Signing with apple_cert: {}'.format(apple_cert_file))
        log.debug('Signing with key: {}'.format(signer_key_file))
        log.debug('Signing with certificate: {}'.format(signer_cert_file))

	# This should have been initialized by our caller
	self.signer = signer

	# This is optional and only used when signing from scratch (but should not be) TODO eliminate
	self.signer_key_file = signer_key_file

	# these arguments are paths to files, and are required
	for filename in [signer_cert_file, apple_cert_file]:
            if not os.path.exists(filename):
                msg = "Can't find {0}".format(filename)
                log.warn(msg)
                raise MissingCredentials(msg)
        self.signer_cert_file = signer_cert_file
        self.apple_cert_file = apple_cert_file

	self.team_id = team_id    # FIXME this seems backwards, we assign then reassign?
        team_id = self.get_team_id()
        if team_id is None:
            raise ImproperCredentials("Cert file does not contain Subject line"
                                      "with Apple Organizational Unit (OU)")

        self.check_openssl_version()

    def check_openssl_version(self):
        openssl_version = get_installed_openssl_version()
        if not is_openssl_version_ok(openssl_version, MINIMUM_OPENSSL_VERSION):
            msg = "Signing may not work: OpenSSL version is {0}, need {1} !"
            log.warn(msg.format(openssl_version, MINIMUM_OPENSSL_VERSION))

    def sign_with_openssl_cms(self, data):
        """ sign data, return string; this is the old way to do it, kept
            around because it's currently the only way to produce a
            signature from scratch, rather than by modifying and
            existing one. """

        cmd = [
            "cms",
            "-sign", "-binary", "-nosmimecap",
            "-certfile", self.apple_cert_file,
            "-signer", self.signer_cert_file,
            "-inkey", self.signer_key_file,
            "-keyform", "pem",
            "-outform", "DER"
        ]
        signature = openssl_command(cmd, data)
        log.debug("in length: {}, out length: {}".format(len(data), len(signature)))
        # in some cases we've seen this return a zero length file.
        # Misconfigured machines?
        if len(signature) < 128:
            too_small_msg = "Command `{0}` returned success, but signature "
            "seems too small ({1} bytes)"
            raise OpenSslFailure(too_small_msg.format(' '.join(cmd),
                                                      len(signature)))
        return signature

    def sign(self, data, oldsig):
	""" sign data, return string. Only modifies an existing CMS structure """

        parsed_sig = asn1crypto.cms.ContentInfo.load(oldsig)

        for signer_info in parsed_sig['content']['signer_infos']:
            # Update signingTime
            signer_info['signed_attrs'][1][1][0] = asn1crypto.cms.Time("utc_time", datetime.utcnow())
            # Update messageDigest
            signer_info['signed_attrs'][2][1][0] = hashlib.sha256(data).digest()

            # This line is necessary to make the next one work! Pretty gross.
            signer_info['signed_attrs'].native
            # Truncate signed_attrs to remove new custom Apple fields, until we can figure out how to update them.
            signer_info['signed_attrs'] = signer_info['signed_attrs'][:3]

            to_sign = signer_info['signed_attrs'].dump()
            to_sign = '1' + to_sign[1:]  # change type from IMPLICIT [0] to EXPLICIT SET OF, per RFC 5652.

	    pkcs1sig = self.signer.sign(to_sign)

            signer_info['signature'] = pkcs1sig

        return parsed_sig.dump()

    def get_common_name(self):
        """ read in our cert, and get our Common Name """
        with open(self.signer_cert_file, 'rb') as fh:
            cert = crypto.load_certificate(crypto.FILETYPE_PEM, fh.read())
        subject = cert.get_subject()
        return dict(subject.get_components())['CN']

    def _log_parsed_asn1(self, data):
        cmd = ['asn1parse', '-inform', 'DER' '-i']
        parsed_asn1 = openssl_command(cmd)
        log.debug(parsed_asn1)

    def get_team_id(self):
        """ Same as Apple Organizational Unit. Should be in the cert """
        if self.team_id:
            return self.team_id

        team_id = None
        cmd = [
            'x509',
            '-in', self.signer_cert_file,
            '-text',
            '-noout'
        ]
        certificate_info = openssl_command(cmd)
        subject_with_ou_match = re.compile(r'\s+Subject:.*OU\s?=\s?(\w+)')
        for line in certificate_info.splitlines():
            match = subject_with_ou_match.match(line)
            if match is not None:
                team_id = match.group(1)
                break
        self.team_id = team_id
        return team_id

    def is_adhoc(self):
        return False

class AdhocCmsSigner(CmsSigner):
    def __init__(self):
        pass

    def sign(self, data):
        """Return empty signature"""
        return ''

    def is_adhoc(self):
        return True

    def get_team_id(self):
        return ''
