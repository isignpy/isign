import archive
import biplist
# import makesig
import exceptions
import glob
import os
from os.path import dirname, exists, expanduser, join, realpath
from signer import Pkcs1Signer, CmsSigner
from provisioner import Provisioner


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


def get_credential_paths(directory, file_names=None):
    """ Given a directory, return dict of paths to standard
        credential files """
    if file_names is None:
        file_names = DEFAULT_CREDENTIAL_FILE_NAMES
    paths = {}
    for (k, file_name) in file_names.iteritems():
        paths[k] = join(directory, file_name)
    return paths


# We will default to using credentials in a particular
# directory with well-known names.
HOME_DIR = expanduser("~")
DEFAULT_CREDENTIAL_PATHS = get_credential_paths(
    join(HOME_DIR, '.isign')
)


def get_entitlements_paths(directory):
    """ Given a directory, return list of entitlements files """
    return glob.glob(join(directory, "*.entitlements"))


def resign_with_creds_dir(input_path,
                          credentials_directory,
                          **kwargs):
    """ Do isign.resign(), but with credential files from this directory """
    kwargs.update(get_credential_paths(credentials_directory))
    kwargs.update(get_entitlements_paths(credentials_directory))
    return resign(input_path, **kwargs)


def resign(input_path,
           deep=True,
           apple_cert=DEFAULT_APPLE_CERT_PATH,
           certificate=DEFAULT_CREDENTIAL_PATHS['certificate'],
           key=DEFAULT_CREDENTIAL_PATHS['key'],
           provisioning_profiles=None,
           output_path=join(os.getcwd(), "out"),
           signer_class=Pkcs1Signer,
           signer_arguments=None,
           info_props=None,
           entitlements_paths=None):
    """ Essentially a wrapper around archive.resign(). We initialize the CmsSigner, entitlements,
        and set default arguments """

    if signer_arguments is None:
        signer_arguments = {}

    if key is not None:
        signer_arguments['keyfile'] = key
    signer = signer_class(**signer_arguments)

    cms_signer = CmsSigner(signer,
                           apple_cert_file=apple_cert,
                           signer_cert_file=certificate)

    if provisioning_profiles is None:
        provisioning_profiles = [DEFAULT_CREDENTIAL_PATHS['provisioning_profile']]

    if entitlements_paths is None:
        entitlements_paths = []

    provisioner = Provisioner(provisioning_profiles, entitlements_paths)
    # TODO sanity check that all provisioning profiles match certificate?

    try:
        return archive.resign(input_path,
                              deep,
                              cms_signer,
                              provisioner,
                              output_path,
                              info_props)
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
