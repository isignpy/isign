""" Represents an app archive. This is an app at rest, whether it's a naked
    app bundle in a directory, or a zipped app bundle, or an IPA. We have a
    common interface to extract these apps to a temp file, then resign them,
    and create an archive of the same type """

import abc
import biplist
from bundle import IosApp
from exceptions import MissingHelpers, NotSignable, NotMatched
from distutils import spawn
import logging
import os
from os.path import abspath, dirname, exists, isdir, isfile, join, normpath
import tempfile
import re
from subprocess import call
import shutil
import zipfile

helper_paths = {}
log = logging.getLogger(__name__)


def get_helper(helper_name):
    """ find paths to executables. Cached in helper_paths """
    if helper_name not in helper_paths or helper_paths[helper_name] is None:
        # note, find_executable returns None is not found
        # in other words, we keep retrying until found
        helper_paths[helper_name] = spawn.find_executable(helper_name)
    log.debug("got executable {} for {}".format(helper_paths[helper_name],
                                                helper_name))
    return helper_paths[helper_name]


def make_temp_dir():
    return tempfile.mkdtemp(prefix="isign-")


class Archive(object):
    __metaclass__ = abc.ABCMeta

    # we use abc.abstractmethod throughout because there are certain class
    # methods we want to ensure are implemented.

    @abc.abstractmethod
    def unarchive_to_temp(self):
        """ Unarchive and copy to a temp directory """
        pass

    @abc.abstractmethod
    def archive(cls, path, output_path):
        """ Archive a directory to an output path """
        pass

    @abc.abstractmethod
    def get_info(cls, path):
        """ Obtain app metadata from Info.plist without unarchiving """
        pass

    @abc.abstractmethod
    def precheck(cls, path):
        """ Check if this is, in fact, an archive of this type """
        pass

    @abc.abstractmethod
    def find_bundle_dir(cls, path):
        """ Locate the directory of the main app (aka bundle) """
        pass


class AppArchive(Archive):
    """ The simplest form of archive -- a naked IosApp Bundle, with no extra directory structure,
        compression, etc """

    @classmethod
    def find_bundle_dir(cls, path):
        """ Included for similarity with the zipped archive classes. In this case, the bundle dir
            *is* the directory """
        return path

    @classmethod
    def _get_plist_path(cls, path):
        return join(cls.find_bundle_dir(path), "Info.plist")

    @classmethod
    def get_info(cls, path):
        return biplist.readPlist(cls._get_plist_path(path))

    @classmethod
    def precheck(cls, path):
        if not isdir(path):
            return False
        if not os.path.exists(cls._get_plist_path(path)):
            return False
        plist = cls.get_info(path)
        is_native = IosApp.is_native(plist)
        log.debug("is_native: {}".format(is_native))
        return is_native

    @classmethod
    def archive(cls, path, output_path):
        if exists(output_path):
            shutil.rmtree(output_path)
        shutil.move(path, output_path)
        log.info("archived %s to %s" % (cls.__name__, output_path))

    def __init__(self, path):
        self.path = path
        self.relative_bundle_dir = '.'
        self.bundle_info = self.get_info(self.path)

    def unarchive_to_temp(self):
        containing_dir = make_temp_dir()
        log.debug("unarchiving to temp... %s -> %s", self.path, containing_dir)
        shutil.rmtree(containing_dir)  # quirk of copytree, top dir can't exist already
        shutil.copytree(self.path, containing_dir)
        return UncompressedArchive(containing_dir, '.', self.__class__)


class AppZipArchive(Archive):
    """ Just like an app, except it's zipped up, and when repackaged,
        should be re-zipped. """
    app_dir_pattern = r'^([^/]+\.app/).*$'
    extensions = ['.zip']
    helpers = ['zip', 'unzip']

    @classmethod
    def is_helpers_present(cls):
        """ returns False if any of our helper apps wasn't found in class init """
        is_present = True
        for helper_name in cls.helpers:
            if get_helper(helper_name) is None:
                log.error("missing helper for class {}: {}".format(cls.__name__, helper_name))
                is_present = False
                break
        return is_present

    @classmethod
    def is_archive_extension_match(cls, path):
        """ does this path have the right extension """
        log.debug('extension match')
        for extension in cls.extensions:
            log.debug('extension match: %s', extension)
            if path.endswith(extension):
                return True
        return False

    @classmethod
    def find_bundle_dir(cls, zipfile_obj):
        relative_bundle_dir = None
        apps = set()
        file_list = zipfile_obj.namelist()
        for file_name in file_list:
            matched = re.match(cls.app_dir_pattern, file_name)
            if matched:
                apps.add(matched.group(1))
        if len(apps) == 1:
            log.debug("found one app")
            relative_bundle_dir = apps.pop()
        elif len(apps) > 1:
            log.warning('more than one app found in archive')
        else:
            log.warning('no apps found in archive')
        return relative_bundle_dir

    @classmethod
    def _get_plist_path(cls, relative_bundle_dir):
        return join(relative_bundle_dir, "Info.plist")

    @classmethod
    def precheck(cls, path):
        """ Checks if an archive looks like this kind of app. Have to examine
            within the zipfile, b/c we don't want to make temp dirs just yet. This
            recapitulates a very similar precheck in the Bundle class """
        if not isfile(path):
            return False
        if not cls.is_helpers_present():
            raise MissingHelpers("helpers not present")
        is_native = False
        log.debug('precheck')
        log.debug('path: %s', path)
        if (cls.is_archive_extension_match(path) and
                zipfile.is_zipfile(path)):
            log.debug("this is an archive, and a zipfile")
            zipfile_obj = zipfile.ZipFile(path)
            relative_bundle_dir = cls.find_bundle_dir(zipfile_obj)
            if relative_bundle_dir is not None:
                plist_path = cls._get_plist_path(relative_bundle_dir)
                if plist_path not in zipfile_obj.namelist():
                    return False
                plist = cls.get_info(relative_bundle_dir, zipfile_obj)
                is_native = IosApp.is_native(plist)
        log.debug("is_native: {}".format(is_native))
        return is_native

    @classmethod
    def get_info(cls, relative_bundle_dir, zipfile_obj):
        plist_path = cls._get_plist_path(relative_bundle_dir)
        plist_bytes = zipfile_obj.read(plist_path)
        return biplist.readPlistFromString(plist_bytes)

    def __init__(self, path):
        self.path = path
        zipfile_obj = zipfile.ZipFile(path)
        self.relative_bundle_dir = self.find_bundle_dir(zipfile_obj)
        self.bundle_info = self.get_info(self.relative_bundle_dir,
                                         zipfile_obj)

    def unarchive_to_temp(self):
        containing_dir = make_temp_dir()
        call([get_helper('unzip'), "-qu", self.path, "-d", containing_dir])
        app_dir = abspath(join(containing_dir, self.relative_bundle_dir))
        return UncompressedArchive(containing_dir, self.relative_bundle_dir, self.__class__)

    @classmethod
    def archive(cls, containing_dir, output_path):
        """ archive this up into a zipfile. Note this is a classmethod, because
            the caller will use us on a temp directory somewhere """
        # the temp file is necessary because zip always adds ".zip" if it
        # does not have an extension. But we want to respect the desired
        # output_path's extension, which could be ".ipa" or who knows.
        # So we move it to the output_path later.
        #
        # We also do a little dance with making another temp directory just
        # to construct the zip file. This is the best way to ensure the an unused
        # filename. Also, `zip` won't overwrite existing files, so this is safer.
        temp_zip_dir = None
        try:
            # need to chdir and use relative paths, because zip is stupid
            temp_zip_dir = tempfile.mkdtemp(prefix="isign-zip-")
            temp_zip_file = join(temp_zip_dir, 'temp.zip')
            call([get_helper('zip'), "-qr", temp_zip_file, "."], cwd=containing_dir)
            shutil.move(temp_zip_file, output_path)
            log.info("archived %s to %s" % (cls.__name__, output_path))
        finally:
            if temp_zip_dir is not None and isdir(temp_zip_dir):
                shutil.rmtree(temp_zip_dir)


class IpaArchive(AppZipArchive):
    """ IPA is Apple's standard for distributing apps. Much like an AppZip,
        but slightly different paths """
    extensions = ['.ipa']
    app_dir_pattern = r'^(Payload/[^/]+\.app/).*$'


class UncompressedArchive(object):
    """ This just keeps track of some state with an unzipped app archive and
        how to re-zip it back up once re-signed. The bundle is located somewhere
        inside the containing directory, but might be a few directories down, like in
        a ContainingDir/Payload/something.app

        This class is also useful if you have an app that's already unzipped and
        you want to sign it. """

    def __init__(self, path, relative_bundle_dir, archive_class):
        """ Path is the "Containing dir", the dir at the root level of the unzipped archive
                (or the dir itself, in the case of an AppArchive archive)
            relative bundle dir is the dir containing the bundle, e.g. Payload/Foo.app
            archive class is the kind of archive this was (Ipa, etc.) """
        self.path = path
        self.relative_bundle_dir = relative_bundle_dir
        self.archive_class = archive_class
        bundle_path = normpath(join(path, relative_bundle_dir))
        self.bundle = IosApp(bundle_path)

    def archive(self, output_path):
        """ Re-zip this back up, or simply copy it out, depending on what the
            original archive class did """
        self.archive_class.archive(self.path, output_path)

    def clone(self, target_path):
        """ Copy the uncompressed archive somewhere else, return initialized
            UncompressedArchive """
        shutil.copytree(self.path, target_path)
        return self.__class__(target_path,
                              self.relative_bundle_dir,
                              self.archive_class)

    def remove(self):
        # the containing dir might be gone already b/c AppArchive simply moves
        # it to the desired target when done
        if exists(self.path) and isdir(self.path):
            log.debug('removing ua: %s', self.path)
            shutil.rmtree(self.path)


def archive_factory(path):
    """ Guess what kind of archive we are dealing with, return an
        archive object. Returns None if path did not match any archive type """
    archive = None
    for cls in [IpaArchive, AppZipArchive, AppArchive]:
        if cls.precheck(path):
            archive = cls(path)
            log.debug("File %s matched as %s", path, cls.__name__)
            break
    return archive


def view(input_path):
    if not exists(input_path):
        raise IOError("{0} not found".format(input_path))
    ua = None
    bundle_info = None
    try:
        archive = archive_factory(input_path)
        if archive is None:
            raise NotMatched('No matching archive type found')
        ua = archive.unarchive_to_temp()
        bundle_info = ua.bundle.info
    finally:
        if ua is not None:
            ua.remove()
    return bundle_info


def resign(input_path,
           deep,
           cms_signer,
           provisioner,
           output_path,
           info_props=None):
    """ Unified interface to extract any kind of archive from
        a temporary file, resign it with these credentials,
        and create a similar archive for that resigned app """

    if not exists(input_path):
        raise IOError("{0} not found".format(input_path))

    ua = None
    bundle_info = None
    try:
        archive = archive_factory(input_path)
        if archive is None:
            raise NotSignable('No matching archive type found')
        ua = archive.unarchive_to_temp()
        if info_props:
            # Override info.plist props of the parent bundle
            ua.bundle.update_info_props(info_props)
        ua.bundle.resign(deep, cms_signer, provisioner)
        bundle_info = ua.bundle.info
        ua.archive(output_path)
    except NotSignable as e:
        msg = "Not signable: <{0}>: {1}\n".format(input_path, e)
        log.info(msg)
        raise
    finally:
        if ua is not None:
            ua.remove()
    return bundle_info
