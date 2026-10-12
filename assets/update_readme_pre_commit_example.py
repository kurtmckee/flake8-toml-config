# This file is a part of flake8-toml-config.
# https://github.com/kurtmckee/flake8-toml-config
# Copyright 2025 Kurt McKee <contactme@kurtmckee.org>
# SPDX-License-Identifier: MIT

import pathlib
import re
import sys
import textwrap
import tomllib

FILES_NOT_MODIFIED = 0
FILES_MODIFIED = 1

ROOT = pathlib.Path(__file__).parent.parent
PRE_COMMIT_YAML = (ROOT / ".pre-commit-config.yaml").resolve()
PYPROJECT_TOML = (ROOT / "pyproject.toml").resolve()
README_RST = (ROOT / "README.rst").resolve()


def main() -> int:
    # Extract the YAML example to embed in the README.
    yaml = PRE_COMMIT_YAML.read_text(encoding="utf-8")
    start_line = "# START_README_EXAMPLE_BLOCK\n"
    end_line = "# END_README_EXAMPLE_BLOCK"
    start = yaml.find(start_line) + len(start_line)
    end = yaml.rfind("\n", start, yaml.find(end_line, start))
    example = textwrap.dedent(yaml[start:end])

    # Inject the current project version.
    project_info = tomllib.loads(PYPROJECT_TOML.read_text())
    version = project_info["project"]["version"]
    example = re.sub(r"""(?<=flake8-toml-config==)[0-9.]+""", version, example)

    # Prepare the example for injection.
    block = "..  code-block:: yaml\n\n" + textwrap.indent(example, " " * 4)

    # Determine the text boundaries of the source code in the README.
    rst = README_RST.read_text(encoding="utf-8")
    start_line = "..  START_EXAMPLE_PRE_COMMIT_BLOCK\n"
    end_line = "..  END_EXAMPLE_PRE_COMMIT_BLOCK"
    start = rst.find(start_line) + len(start_line)
    end = rst.rfind("\n", start, rst.find(end_line, start))

    # Inject the example and determine if the README needs to be overwritten.
    new_rst = rst[:start] + block + rst[end:]
    if new_rst != rst:
        README_RST.write_text(new_rst, encoding="utf-8", newline="\n")
        return FILES_MODIFIED

    return FILES_NOT_MODIFIED


if __name__ == "__main__":
    sys.exit(main())
