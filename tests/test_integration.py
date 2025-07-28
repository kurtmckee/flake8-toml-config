# This file is a part of flake8-toml-config.
# https://github.com/kurtmckee/flake8-toml-config
# Copyright 2025 Kurt McKee <contactme@kurtmckee.org>
# SPDX-License-Identifier: MIT

from __future__ import annotations

import os
import pathlib
import subprocess

import pytest

root = pathlib.Path(__file__).parent.parent
assets = root / "tests/assets"


def run_flake8(
    config_name: str, trailing: list[str] | None = None
) -> subprocess.CompletedProcess[str]:
    command = [
        "flake8",
        "--config",
        assets / f"{config_name}.toml",
    ]
    if trailing:
        command.extend(trailing)
    else:
        command.extend(["--", assets / f"{config_name}.py"])

    env = os.environ.copy()
    env["COVERAGE_PROCESS_START"] = "pyproject.toml"
    return subprocess.run(
        args=command,
        env=env,
        encoding="utf-8",
        capture_output=True,
    )


def test_integration_no_op():
    """Verify that integration is possible.

    The bar is low: flake8 should successfully load this plugin
    and evaluate an empty file. Success is defined as "no errors".
    """

    process = run_flake8("no-op")
    assert process.stdout == ""
    assert process.returncode == 0, process.stderr
    assert process.stderr == ""


def test_integration_config_change():
    """Verify that the configuration can be changed at all.

    This is accomplished by configuring the max-line-length to a small value
    in a TOML file and confirming that flake8 is unhappy with line lengths.
    """

    process = run_flake8("long-line")
    assert "E501 line too long (59 > 40 characters)" in process.stdout, process.stderr
    assert process.returncode == 1
    assert process.stderr == ""


@pytest.mark.parametrize("config_name", ("native", "verbose", "strings"))
def test_local_plugin(config_name):
    """Verify that a local plugin can be loaded."""

    process = run_flake8(f"local-plugin-{config_name}", ["--help"])
    assert "--local-plugin-option" in process.stdout, process.stderr
    assert "The demo local plugin was loaded successfully." in process.stdout
    assert process.returncode == 0
    assert process.stderr == ""
