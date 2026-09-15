"""Set the website key in addons manifests."""
import re

import click

from .manifest import get_manifest_path, iter_addon_dirs, parse_manifest


WEBSITE_KEY_RE = re.compile(r"""(["']website["']\s*:\s*["'])([^"']*)(["'])""")


@click.command()
@click.argument("url")
@click.option("--addons-dir", default=".")
@click.option(
    "--exclude",
    multiple=True,
    metavar="PATTERN",
    help="Addon name or glob to leave untouched (repeatable). "
    "Use it for vendored third-party addons.",
)
def main(url, addons_dir, exclude):
    for addon_name, addon_dir in iter_addon_dirs(addons_dir, exclude):
        manifest_path = get_manifest_path(addon_dir)
        try:
            with open(manifest_path) as manifest_file:
                manifest = parse_manifest(manifest_file.read())
        except Exception:
            raise click.ClickException(
                "Error parsing manifest {}.".format(manifest_path)
            )
        if "website" not in manifest:
            raise click.ClickException(
                "website key not found in manifest in {}.".format(addon_name)
            )
        with open(manifest_path) as manifest_file:
            manifest_str = manifest_file.read()
        new_manifest_str, n = WEBSITE_KEY_RE.subn(
            r"\g<1>" + url + r"\g<3>", manifest_str
        )
        if n == 0:
            raise click.ClickException(
                "no website key match in manifest in {}.".format(addon_name)
            )
        if n > 1:
            raise click.ClickException(
                "more than one website key match in manifest in {}.".format(addon_name)
            )
        if new_manifest_str != manifest_str:
            with open(manifest_path, "w") as manifest_file:
                manifest_file.write(new_manifest_str)
