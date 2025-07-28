# This file is a part of flake8-toml-config.
# https://github.com/kurtmckee/flake8-toml-config
# Copyright 2025 Kurt McKee <contactme@kurtmckee.org>
# SPDX-License-Identifier: MIT

import sys

__all__ = ("tomllib",)

if sys.version_info >= (3, 11):
    import tomllib
else:
    import tomli as tomllib
