# This file is a part of flake8-toml-config.
# https://github.com/kurtmckee/flake8-toml-config
# Copyright 2025 Kurt McKee <contactme@kurtmckee.org>
# SPDX-License-Identifier: MIT

import configparser
import os
import pathlib

import flake8.exceptions
import pytest

import flake8_toml_config.config as config


@pytest.mark.parametrize(
    "contents",
    (
        pytest.param("", id="empty"),
        pytest.param("[tool]", id="`tool` without `flake8` section"),
        pytest.param("[tool.flake8]", id="empty `flake8`"),
        pytest.param(
            '[tool."flake8:local-plugins"]', id="empty `flake8:local-plugins`"
        ),
    ),
)
def test_load_config_empty_file_success(fs, contents):
    fs.create_file("pyproject.toml", contents=contents)
    parser, path = config.load_config("pyproject.toml", [])
    assert path == str(pathlib.Path("/").absolute())
    assert "flake8" in parser
    assert "flake8:local-plugins" in parser


def test_load_config_no_files(fs):
    parser, path = config.load_config(None, [])
    assert path == str(pathlib.Path("/").absolute())
    assert "flake8" in parser
    assert "flake8:local-plugins" in parser


def test_load_config_auto_find(fs, monkeypatch):
    contents = "[tool.flake8]\nmax-line-length = 40"
    fs.create_file("/cwd/pyproject.toml", contents=contents)
    monkeypatch.chdir("/cwd")
    parser, path = config.load_config(None, [])
    assert parser["flake8"]["max-line-length"] == "40"
    assert path == str(pathlib.Path("/cwd").absolute())


def test_load_config_extras(fs, monkeypatch):
    contents = "[tool.flake8]\nmax-line-length = 40"
    fs.create_file("/subdir/pyproject.toml", contents=contents)
    contents = "[tool.flake8]\nextend-exclude = ['E501']"
    fs.create_file("/custom/local.toml", contents=contents)
    parser, path = config.load_config("/subdir/pyproject.toml", ["/custom/local.toml"])
    assert parser["flake8"]["max-line-length"] == "40"
    assert parser["flake8"]["extend-exclude"] == "E501"
    assert path == str(pathlib.Path("/subdir").absolute())


def test_load_config_isolated_mode(monkeypatch, fs):
    fs.create_file("custom.toml", contents="[tool.flake8]\nmax-line-length = 40")
    fs.create_file("pyproject.toml", contents="[tool.flake8]\nmax-line-length = 50")
    parser, path = config.load_config("custom.toml", [], isolated=True)

    assert path == os.path.abspath(os.curdir)
    assert "flake8" not in parser


@pytest.mark.parametrize(
    "contents, match",
    (
        pytest.param(None, "file does not exist", id="bad --config option"),
        pytest.param(b"\xff", "could not be decoded", id="UnicodeDecodeError"),
        pytest.param("bogus!", "could not be parsed", id="TOMLDecodeError"),
        pytest.param("tool = 1", "not a dict", id="non-dict `tool` value"),
        pytest.param("tool.flake8 = 1", "not a dict", id="non-dict flake8"),
        pytest.param(
            'tool."flake8:local-plugins" = 1',
            "not a dict",
            id="non-dict flake8:local-plugins",
        ),
    ),
)
def test_read_toml_corruptions(fs, contents, match):
    if contents is not None:
        fs.create_file("pyproject.toml", contents=contents)
    with pytest.raises(flake8.exceptions.ExecutionError, match=match):
        config._read_toml(pathlib.Path("pyproject.toml"))


def test_read_toml_return_value(fs):
    fs.create_file("pyproject.toml")
    result = config._read_toml(pathlib.Path("pyproject.toml"))
    assert result == {
        "flake8": {},
        "flake8:local-plugins": {},
    }


@pytest.mark.parametrize(
    "section, key, value, expected_value",
    (
        pytest.param("flake8", "max-line-length", 78, "78", id="int"),
        pytest.param("flake8", "max-line-length", "78", "78", id="str"),
        pytest.param(
            "flake8", "extend-exclude", ["A101", "A102"], "A101\nA102", id="list[str]"
        ),
        pytest.param(
            "flake8", "extend-exclude", "A101\nA102", "A101\nA102", id="list as str"
        ),
        pytest.param(
            "flake8:local-plugins",
            "extension",
            {"X": "x:Plugin", "Y": "y:Plugin"},
            "X = x:Plugin\nY = y:Plugin",
            id="dict[str, str]",
        ),
    ),
)
def test_update_parser_value_conversions(section, key, value, expected_value):
    parser = configparser.RawConfigParser()
    toml_config = {section: {key: value}}
    config._update_parser(parser, toml_config)

    assert parser[section][key] == expected_value


def test_update_parser_section_overwrites():
    parser = configparser.RawConfigParser()
    config_1 = {
        "flake8": {"max-line-length": 10},
        "flake8:local-plugins": {},
    }
    config_2 = {
        "flake8": {"extend-ignore": ["E501"]},
        "flake8:local-plugins": {},
    }
    config._update_parser(parser, config_1)
    config._update_parser(parser, config_2)
    assert parser["flake8"]["max-line-length"] == "10"
    assert parser["flake8"]["extend-ignore"] == "E501"


@pytest.mark.parametrize(
    "section, key, value, expected_error",
    (
        pytest.param(
            "flake8", "top-level", ..., "value type is not supported", id="top-level"
        ),
        pytest.param(
            "flake8",
            "list",
            [...],
            "list value types are not supported",
            id="list[...]",
        ),
    ),
)
def test_update_parser_type_rejections(section, key, value, expected_error):
    parser = configparser.RawConfigParser()
    toml_config = {section: {key: value}}
    with pytest.raises(flake8.exceptions.ExecutionError, match=expected_error):
        config._update_parser(parser, toml_config)
