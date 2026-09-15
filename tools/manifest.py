# Copyright (c) 2015-2018 ACSONE SA/NV
# License AGPLv3 (https://www.gnu.org/licenses/agpl-3.0-standalone.html)

import ast
import fnmatch
import os

MANIFEST_NAMES = ('__manifest__.py', '__openerp__.py', '__terp__.py')


class NoManifestFound(Exception):
    pass


def get_manifest_path(addon_dir):
    for manifest_name in MANIFEST_NAMES:
        manifest_path = os.path.join(addon_dir, manifest_name)
        if os.path.isfile(manifest_path):
            return manifest_path


def parse_manifest(s):
    return ast.literal_eval(s)


def read_manifest(addon_dir):
    manifest_path = get_manifest_path(addon_dir)
    if not manifest_path:
        raise NoManifestFound("no Odoo manifest found in %s" % addon_dir)
    with open(manifest_path) as mf:
        return parse_manifest(mf.read())


def is_excluded(addon_name, exclude=()):
    """ Whether an addon name matches one of the exclusion patterns.

    Patterns are matched against the addon directory name with fnmatch, so both
    exact names ("pan_ai_pro") and globs ("queue_job*") work.
    """
    return any(fnmatch.fnmatch(addon_name, pattern) for pattern in exclude or ())


def iter_addon_dirs(addons_dir, exclude=()):
    """ Yield (addon_name, addon_dir) for each subdirectory holding a manifest.

    Addons whose name matches one of the `exclude` patterns are skipped. Use it
    to leave vendored third-party addons untouched: the tools of this package
    walk the addons directory themselves (pre-commit runs them with
    `pass_filenames: false`), so the `exclude` key of .pre-commit-config.yaml
    does not reach them.
    """
    for addon_name in sorted(os.listdir(addons_dir)):
        if is_excluded(addon_name, exclude):
            continue
        addon_dir = os.path.join(addons_dir, addon_name)
        if get_manifest_path(addon_dir):
            yield addon_name, addon_dir


def find_addons(addons_dir, installable_only=True, exclude=()):
    """ yield (addon_name, addon_dir, manifest) """
    for addon_name in os.listdir(addons_dir):
        if is_excluded(addon_name, exclude):
            continue
        addon_dir = os.path.join(addons_dir, addon_name)
        try:
            manifest = read_manifest(addon_dir)
        except NoManifestFound:
            continue
        if installable_only and not manifest.get('installable', True):
            continue
        yield addon_name, addon_dir, manifest
