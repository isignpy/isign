__version__ = '1.0.0'

import logging

log = logging.getLogger(__name__)


class FooSigner(object):
    def __init__(self,
                 signer_key_file=None,
                 signer_cert_file=None,
                 apple_cert_file=None,
                 team_id=None,
                 signer_args=None):
        self.key = signer_key_file
        self.certificate = signer_cert_file,
        self.apple_certificate = apple_cert_file,
        self.team_id = team_id,
        self.signer_args = signer_args

    def sign(self, data):
        log.info("I am FooSigning!")
        log.info(self.signer_args)
        self.signer_args.callback()
        return ''

    def is_adhoc(self):
        return False