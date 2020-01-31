""" This is for a few random commands we either can't or haven't figured out how to do
    with crypto libraries """

from distutils import spawn
from exceptions import OpenSslFailure
import logging
import os
import re
import subprocess



OPENSSL = os.getenv('OPENSSL', spawn.find_executable('openssl', os.getenv('PATH', '')))
# modern OpenSSL versions look like '0.9.8zd'. Use a regex to parse
OPENSSL_VERSION_RE = re.compile(r'(\d+).(\d+).(\d+)(\w*)')
MINIMUM_OPENSSL_VERSION = '1.0.1'

log = logging.getLogger(__name__)


class OpenSslShell(object):
    @classmethod
    def command(cls, args, data=None, expect_err=False):
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

    @classmethod
    def get_installed_version(cls):
        version_line = cls.command(['version'])
        # e.g. 'OpenSSL 0.9.8zd 8 Jan 2015'
        return re.split(r'\s+', version_line)[1]

    @classmethod
    def is_version_ok(cls, version, minimum):
        """ check that the openssl tool is at least a certain version """
        version_tuple = cls.version_to_tuple(version)
        minimum_tuple = cls.version_to_tuple(minimum)
        return version_tuple >= minimum_tuple

    @classmethod
    def version_to_tuple(cls, s):
        """ OpenSSL uses its own versioning scheme, so we convert to tuple,
            for easier comparison """
        search = re.search(OPENSSL_VERSION_RE, s)
        if search is not None:
            return search.groups()
        return ()

    @classmethod
    def check_version(cls):
        openssl_version = cls.get_installed_version()
        if not cls.is_version_ok(openssl_version, MINIMUM_OPENSSL_VERSION):
            msg = "Signing may not work: OpenSSL version is {0}, need {1} !"
            log.warn(msg.format(openssl_version, MINIMUM_OPENSSL_VERSION))