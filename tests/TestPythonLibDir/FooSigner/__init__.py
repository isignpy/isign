__version__ = '1.0.0'

import logging

log = logging.getLogger(__name__)


class FooSigner(object):
    def __init__(self,
                 signer_key_file=None,
                 signer_cert_file=None,
                 apple_cert_file=None,
                 team_id=None,
                 callback=None):
        self.key = signer_key_file
        self.certificate = signer_cert_file
        self.apple_certificate = apple_cert_file
        self.team_id = team_id
        self.callback = callback

    def sign(self, data):
        log.info("I am FooSigning, with this callback...")
        log.info(self.callback)
        self.callback("FooSigner was here")
        return ''

    def is_adhoc(self):
        return False

    def get_team_id(self):
        return 'FOOCMPNY'

    def get_common_name(self):
        return 'FooCompany'