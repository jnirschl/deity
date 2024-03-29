# DeITy

De-Identification Toolkit (DeITy) is a simple python package for deidentifying
files that may contain sensitive identifiers by replacing them with an
alphanumeric identifier.

<!---
[![PyPI](https://img.shields.io/pypi/v/deity.svg)][pypi_]
[![Status](https://img.shields.io/pypi/status/deity.svg)][status]
[![Python Version](https://img.shields.io/pypi/pyversions/deity)][python version]
[![License](https://img.shields.io/pypi/l/deity)][license]

[![Read the documentation at https://deity.readthedocs.io/](https://img.shields.io/readthedocs/deity/latest.svg?label=Read%20the%20Docs)][read the docs]
[![Tests](https://github.com/jnirschl/deity/workflows/Tests/badge.svg)][tests]
--->

[![Codecov](https://codecov.io/gh/jnirschl/deity/branch/main/graph/badge.svg)][codecov]
[![pre-commit](https://img.shields.io/badge/pre--commit-enabled-brightgreen?logo=pre-commit&logoColor=white)][pre-commit]
[![Black](https://img.shields.io/badge/code%20style-black-000000.svg)][black]

[pypi_]: https://pypi.org/project/deity/
[status]: https://pypi.org/project/deity/
[python version]: https://pypi.org/project/deity
[read the docs]: https://deity.readthedocs.io/
[tests]: https://github.com/jnirschl/deity/actions?workflow=Tests
[codecov]: https://app.codecov.io/gh/jnirschl/deity
[pre-commit]: https://github.com/pre-commit/pre-commit
[black]: https://github.com/psf/black

## Features

-   De-identify files containing sensitive identifiers and replace with a hashed identifier
-   Stores the mapping of identifiers to hashed identifiers in a SQLite database.

## Requirements

-   See pyproject.toml

## Installation

You can install _DeITy_ via [pip] from [PyPI]:

```console
$ pip install deity
```

## Usage

Please see the [Command-line Reference] for details.

## Contributing

Contributions are very welcome.
To learn more, see the [Contributor Guide].

## License

Distributed under the terms of the [MIT license][license],
_DeITy_ is free and open source software.

## Issues

If you encounter any problems,
please [file an issue] along with a detailed description.

## Credits

This project was generated from [@cjolowicz]'s [Hypermodern Python Cookiecutter] template.

[@cjolowicz]: https://github.com/cjolowicz
[pypi]: https://pypi.org/
[hypermodern python cookiecutter]: https://github.com/cjolowicz/cookiecutter-hypermodern-python
[file an issue]: https://github.com/jnirschl/deity/issues
[pip]: https://pip.pypa.io/

<!-- github-only -->

[license]: https://github.com/jnirschl/deity/blob/main/LICENSE
[contributor guide]: https://github.com/jnirschl/deity/blob/main/CONTRIBUTING.md
[command-line reference]: https://deity.readthedocs.io/en/latest/usage.html
