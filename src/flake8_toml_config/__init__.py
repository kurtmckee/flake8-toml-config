# This file is a part of flake8-toml-config.
# https://github.com/kurtmckee/flake8-toml-config
# Copyright 2025 Kurt McKee <contactme@kurtmckee.org>
# SPDX-License-Identifier: MIT

from __future__ import annotations

from .config import load_config


def inject() -> None:
    import flake8.options.config

    flake8.options.config.load_config = load_config
