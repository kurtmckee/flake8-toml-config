# This file is a part of flake8-toml-config.
# https://github.com/kurtmckee/flake8-toml-config
# Copyright 2025 Kurt McKee <contactme@kurtmckee.org>
# SPDX-License-Identifier: MIT

from __future__ import annotations

import typing

from flake8.options.manager import OptionManager


class Plugin:
    name = "demo-local-plugin"
    version = "1.0.0"

    @staticmethod
    def add_options(option_manager: OptionManager) -> OptionManager:
        option_manager.add_option(
            long_option_name="--local-plugin-option",
            help="The demo local plugin was loaded successfully.",
            parse_from_config=False,
            comma_separated_list=False,
            normalize_paths=True,
        )
        return option_manager

    def __init__(self, tree: None) -> None:
        pass  # pragma: nocover

    @staticmethod
    def run() -> typing.Iterable[None]:
        return iter(())  # pragma: nocover
