import archive
# import makesig
import exceptions
import importlib
import os
from os.path import dirname, exists, expanduser, join, realpath
from signer import AdhocSigner, Signer


# this comes with the repo
PACKAGE_ROOT = dirname(realpath(__file__))
DEFAULT_APPLE_CERT_PATH = join(PACKAGE_ROOT, 'apple_credentials', 'applecerts.pem')
DEFAULT_CREDENTIAL_FILE_NAMES = {
    'certificate': 'certificate.pem',
    'key': 'key.pem',
    'provisioning_profile': 'isign.mobileprovision'
}


class NotSignable(Exception):
    """ This is just so we don't expose other sorts of exceptions """
    pass


def get_credential_paths(directory, file_names=DEFAULT_CREDENTIAL_FILE_NAMES):
    """ Given a directory, return dict of paths to standard
        credential files """
    paths = {}
    for (k, file_name) in file_names.iteritems():
        paths[k] = join(directory, file_name)
    return paths


# We will default to using credentials in a particular
# directory with well-known names. This is complicated because
# the old way at Sauce Labs (pre-2017) was:
#   ~/isign-credentials/mobdev.cert.pem, etc.
# But the new way that everyone should now use:
#   ~/.isign/certificate.pem, etc.
HOME_DIR = expanduser("~")
if exists(join(HOME_DIR, 'isign-credentials')):
    DEFAULT_CREDENTIAL_PATHS = get_credential_paths(
        join(HOME_DIR, 'isign-credentials'),
        {
            'certificate': 'mobdev.cert.pem',
            'key': 'mobdev.key.pem',
            'provisioning_profile': 'mobdev1.mobileprovision'
        }
    )
else:
    DEFAULT_CREDENTIAL_PATHS = get_credential_paths(
        join(HOME_DIR, '.isign')
    )


def import_class(name):
    components = name.split('.')
    module_name = '.'.join(components[0:-1])
    class_name = components[-1]
    mod = __import__(module_name, fromlist=[class_name])
    return getattr(mod, class_name)


def get_signer(apple_cert, certificate, key, signer_module, signer_module_arguments):
    """ From a set of arguments to resign(), make an appropriate Signer """
    if signer_module:
        # This could raise an ImportException but we'll let the exception bubble
        signerClass = import_class(signer_module)
        signer = signerClass(apple_cert_file=apple_cert,
                             signer_cert_file=certificate,
                             signer_key_file=key,
                             signer_args=signer_module_arguments)
    else:
        if key:
            signer = Signer(signer_cert_file=certificate,
                            signer_key_file=key,
                            apple_cert_file=apple_cert)
        else:
            signer = AdHocSigner()
    return signer


def resign_with_creds_dir(input_path,
                          credentials_directory,
                          **kwargs):
    """ Do isign.resign(), but with credential files from this directory """
    kwargs.update(get_credential_paths(credentials_directory))
    return resign(input_path, **kwargs)


def resign(input_path,
           deep=True,
           apple_cert=DEFAULT_APPLE_CERT_PATH,
           certificate=DEFAULT_CREDENTIAL_PATHS['certificate'],
           key=DEFAULT_CREDENTIAL_PATHS['key'],
           provisioning_profile=DEFAULT_CREDENTIAL_PATHS['provisioning_profile'],
           output_path=join(os.getcwd(), "out"),
           signer_module=None,
           signer_module_arguments=None,
           info_props=None,
           alternate_entitlements_path=None):
    """ Essentially a wrapper around archive.resign(). We initialize the Signer and set default arguments """
    signer = get_signer(apple_cert, certificate, key, signer_module, signer_module_arguments)

    try:
        return archive.resign(input_path,
                              deep,
                              signer,
                              provisioning_profile,
                              output_path,
                              info_props,
                              alternate_entitlements_path)
    except exceptions.NotSignable as e:
        # re-raise the exception without exposing internal
        # details of how it happened
        raise NotSignable(e)


def view(input_path):
    """ Obtain information about the app """
    try:
        return archive.view(input_path)
    except exceptions.NotSignable as e:
        raise NotSignable(e)
