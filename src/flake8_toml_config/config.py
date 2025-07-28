# This file is a part of flake8-toml-config.
# https://github.com/kurtmckee/flake8-toml-config
# Copyright 2025 Kurt McKee <contactme@kurtmckee.org>
# SPDX-License-Identifier: MIT

from __future__ import annotations

import configparser
import pathlib
import typing

import flake8.exceptions

from ._compat import tomllib


def load_config(
    config: str | None,
    extra: list[str],
    *,
    isolated: bool = False,
) -> tuple[configparser.RawConfigParser, str]:
    """
    Load the config from a TOML file.

    If the `--config` option is passed at the command line,
    the specified TOML file will be used as the primary TOML config.
    Otherwise, `pyproject.toml` in the current working directory will be preferred.

    :param config:
        The path to a TOML file to read config from.
        This is sourced from the CLI option `--config`.
    :param extra:
        A list of additional file paths to read config from.
        This is sourced from the CLI option `--append-config`.
    :param isolated:
        If true, no TOML files will be read, regardless of other CLI options passed.
    :returns:
        For compatibility with flake8's internal structures,
        the return value is a tuple of a RawConfigParser instance
        (even though only TOML files will be read)
        and a string path to the directory containing the primary TOML file.
    """

    cfg = configparser.RawConfigParser()
    cwd = pathlib.Path.cwd()

    # If `--isolated` was specified, return an empty config.
    if isolated:
        return cfg, str(cwd)

    file: pathlib.Path | None = pathlib.Path(config).absolute() if config else None

    # If no config file was specified, search for one.
    if file is None:
        path = cwd / "pyproject.toml"
        if path.is_file():
            file = path

    if file is not None:
        toml_config = _read_toml(file)
        _update_parser(cfg, toml_config)
        cfg_dir = str(file.parent)
    else:
        _update_parser(cfg, {})
        cfg_dir = str(cwd)

    # Read any additional config files.
    for filename in extra:
        file = pathlib.Path(filename)
        extra_config = _read_toml(file)
        _update_parser(cfg, extra_config)

    return cfg, cfg_dir


def _read_toml(file: pathlib.Path) -> dict[str, typing.Any]:
    try:
        all_config = tomllib.loads(file.read_text(encoding="utf-8"))
    except OSError:
        msg = f"The specified config file does not exist: {file}"
        raise flake8.exceptions.ExecutionError(msg)
    except UnicodeDecodeError:
        msg = f"The file at {file!r} could not be decoded as valid Unicode."
        raise flake8.exceptions.ExecutionError(msg) from None
    except tomllib.TOMLDecodeError:
        msg = f"The file at {file!r} could not be parsed as valid TOML."
        raise flake8.exceptions.ExecutionError(msg) from None

    tool_config = all_config.get("tool", {})
    if not isinstance(tool_config, dict):
        msg = f"The `tool` config in {file!r} is not a dict."
        raise flake8.exceptions.ExecutionError(msg)
    flake8_config = tool_config.get("flake8", {})
    if not isinstance(flake8_config, dict):
        msg = f"The `tool.flake8` config in {file!r} is not a dict."
        raise flake8.exceptions.ExecutionError(msg)
    local_plugins_config = tool_config.get("flake8:local-plugins", {})
    if not isinstance(local_plugins_config, dict):
        msg = f'The `tool."flake8:local-plugins"` config in {file!r} is not a dict.'
        raise flake8.exceptions.ExecutionError(msg)

    return {
        "flake8": flake8_config,
        "flake8:local-plugins": local_plugins_config,
    }


def _update_parser(
    parser: configparser.RawConfigParser, config: dict[str, typing.Any]
) -> None:
    """Transform a config dict's values into strings that flake8 can parse correctly.

    Example: [flake8] `extend-ignore` key

        TOML value: ["E203", "E501", "E701"]
        str value:  "E203\nE501\nE701"

    Example: [flake8:local-plugins] `extension` key

        TOML value: {"CRL": "custom_repo_linter:Plugin"}
        str value:  "CRL = custom_repo_linter:Plugin"

    """

    for section in ("flake8", "flake8:local-plugins"):
        if section not in parser:
            parser[section] = {}
        for key, value in config.get(section, {}).items():
            if isinstance(value, list):
                if all(isinstance(v, (str, int, float)) for v in value):
                    transformed_value = "\n".join(value)
                    parser[section][key] = transformed_value
                else:
                    msg = (
                        f"The {section}.{key} list value types are not supported."
                        " They should all be str/int/float types."
                    )
                    raise flake8.exceptions.ExecutionError(msg)
            elif isinstance(value, dict):
                transformed_value = "\n".join(f"{k} = {v}" for k, v in value.items())
                parser[section][key] = transformed_value
            elif isinstance(value, (str, int, float)):
                transformed_value = str(value)
                parser[section][key] = transformed_value
            else:
                msg = (
                    f"The {section}.{key} value type is not supported."
                    " It should be a list, a dict, or a str/int/float type."
                )
                raise flake8.exceptions.ExecutionError(msg)
