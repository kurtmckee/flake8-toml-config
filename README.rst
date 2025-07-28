..
    This file is a part of flake8-toml-config.
    https://github.com/kurtmckee/flake8-toml-config
    Copyright 2025 Kurt McKee <contactme@kurtmckee.org>
    SPDX-License-Identifier: MIT

flake8-toml-config
#####################

Configure flake8 via ``pyproject.toml``. Supports local plugins.

-------------------------------------------------------------------------------

This `flake8`_ plugin adds support for loading the flake8 configuration
from ``pyproject.toml`` files, including loading local plugins.

The plugin will automatically find a ``pyproject.toml`` file
in the current working directory where ``flake8`` is run from.
It also overrides the ``--config`` CLI option
so that a TOML file can be specified to load the config from:

..  code-block:: text

    flake8 --config custom.toml

``flake8-toml-config`` will respect the ``--isolated`` flag.

Note that this plugin replaces flake8's built-in support for other config file formats.
While the plugin is installed, config can only be read from TOML files.


..  _table-of-contents:

Table of contents
=================

*   `Configuration translation <#configuration-translation>`_
*   `pipx usage <#pipx-usage>`_
*   `pre-commit usage <#pre-commit-usage>`_


..  _configuration-translation:

Configuration translation
=========================

Below is an example of a flake8 configuration as it would appear in a ``.flake8`` file:

..  code-block:: ini

    [flake8]
    max-line-length = 80
    extend-select = B950
    extend-ignore = E203,E501,E701

    [flake8:local-plugins]
    paths = ./assets/flake8
    extension =
        CL1 = custom_repo_linter:Plugin1
        CL2 = custom_repo_linter:Plugin2
    reporter =
        CR = custom_repo_reporter:Plugin


Below is the equivalent configuration, suitable for use in a ``pyproject.toml`` file.
Note that the ``flake8:local-plugins`` section requires quotes in the TOML format:

..  code-block:: toml

    [tool.flake8]
    max-line-length = 80
    extend-select = ["B950"]
    extend-ignore = ["E203", "E501", "E701"]

    [tool."flake8:local-plugins"]
    paths = ["./assets/flake8"]
    extension.CL1 = "custom_repo_linter:Plugin1"
    extension.CL2 = "custom_repo_linter:Plugin2"
    reporter.CR = "custom_repo_reporter:Plugin"


Alternatively, multi-line TOML strings can be used for clearer config parity:

..  code-block:: toml

    # ...
    [tool."flake8:local-plugins"]
    paths = ["./assets/flake8"]
    extension = """
        CL1 = custom_repo_linter:Plugin1
        CL2 = custom_repo_linter:Plugin2
    """
    reporter = """
        CR = custom_repo_reporter:Plugin
    """


..  _pipx-usage:

pipx usage
==========

If flake8 is installed using pipx, you can inject this plugin:

..  code-block::

    pipx inject flake8 flake8-toml-config


..  _pre-commit-usage:

pre-commit usage
================

Add this plugin as an additional dependency:

..  code-block:: yaml

    - repo: "https://github.com/pycqa/flake8"
      rev: "7.3.0"
      hooks:
        - id: "flake8"
          additional_dependencies:
            - "flake8-toml-config==1.0.0"


Note that the ``pre-commit autoupdate`` command, and `pre-commit.ci`_,
do not update additional dependencies.
Consider using `upadup`_ to auto-update additional dependencies as needed.


..  Links
..  -----
..
..  _flake8: https://flake8.pycqa.org/
..  _upadup: https://github.com/sirosen/upadup
..  _pre-commit.ci: https://pre-commit.ci
