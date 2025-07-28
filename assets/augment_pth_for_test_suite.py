# This file is a part of flake8-toml-config.
# https://github.com/kurtmckee/flake8-toml-config
# Copyright 2025 Kurt McKee <contactme@kurtmckee.org>
# SPDX-License-Identifier: MIT

import os
import pathlib
import site
import sys
import typing

RC_SUCCESS: typing.Literal[0] = 0
RC_FAILURE: typing.Literal[1] = 1


def main() -> typing.Literal[0, 1]:
    """Ensure coverage starts before importing anything else."""

    tox_env_dir = pathlib.Path(os.environ["TOX_ENV_DIR"])
    for candidate in site.getsitepackages():
        site_package = pathlib.Path(candidate).absolute()
        if tox_env_dir in site_package.parents:
            break
    else:
        print("Unable to find the tox environment's site-packages directory.")
        return RC_FAILURE

    # If the plugin and coverage aren't installed in the tox environment,
    # tox is running this script in an unexpected environment.
    file = site_package / "flake8-toml-config-injector.pth"
    if not file.is_file() and (site_package / "coverage").is_dir():
        return RC_FAILURE

    # Write the `.pth` file if it doesn't already have the required prelude.
    required_prelude = "import coverage; coverage.process_startup()\n"
    contents = file.read_text()
    if not contents.startswith(required_prelude):
        file.write_text(required_prelude + contents)

    return RC_SUCCESS


if __name__ == "__main__":
    sys.exit(main())
