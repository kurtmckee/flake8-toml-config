..
    This file is a part of flake8-toml-config.
    https://github.com/kurtmckee/flake8-toml-config
    Copyright 2025 Kurt McKee <contactme@kurtmckee.org>
    SPDX-License-Identifier: MIT

``requirements/``
#################

This directory contains the files that manage dependencies for the project.

At the time of writing, Poetry supports discrete dependency groups
but always resolves dependencies coherently across all groups.
However, in some cases, dependencies do not need to be coherently resolved;
for example, mypy's dependencies often do not need to be resolved
with other dependency groups.

Each subdirectory in this directory contains a ``pyproject.toml`` file
with purpose-specific dependencies listed.


How it's used
=============

Tox is configured to use the exported ``requirements.txt`` files as needed.


How it's updated
================

A tox label, ``update``, ensures that dependencies can be easily updated,
and that ``requirements.txt`` files are consistently re-exported.

This can be invoked by running:

..  code-block::

    tox run -m update


How to add dependencies
=======================

New dependencies can be added to a given subdirectory's ``pyproject.toml``
by either manually modifying the file, or by running a command like:

..  code-block::

    poetry add --lock --directory "requirements/$DIR" $DEPENDENCY_NAME

Either way, the dependencies must be re-exported:

..  code-block::

    tox run -m update
