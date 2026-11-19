Welcome to Maykin's API clients documentation
=============================================

|build-status| |code-quality| |ruff| |coverage| |docs|

|python-versions| |pypi-version|

Feature-complete clients for APIs in the Dutch government API landscape.

Features
========

* Resource-driven Python API, e.g. ``cases_client.case.create(...)``
* Fully type-annotated for type safety and editor autocomplete support
* Built on top of requests and `msgspec <https://msgspec.dev/>`_
* Bring your own types if you want
* Only import what you need - zero overhead for unused clients.

.. toctree::
   :maxdepth: 2

   quickstart
   changelog

.. |build-status| image:: https://github.com/maykinmedia/maykin-api-clients/actions/workflows/ci.yml/badge.svg
    :alt: Build status
    :target: https://github.com/maykinmedia/maykin-api-clients/actions/workflows/ci.yml

.. |code-quality| image:: https://github.com/maykinmedia/maykin-api-clients/actions/workflows/code-quality.yml/badge.svg
     :alt: Code quality checks
     :target: https://github.com/maykinmedia/maykin-api-clients/actions/workflows/code-quality.yml

.. |ruff| image:: https://img.shields.io/endpoint?url=https://raw.githubusercontent.com/astral-sh/ruff/main/assets/badge/v2.json
    :target: https://github.com/astral-sh/ruff
    :alt: Ruff

.. |coverage| image:: https://codecov.io/gh/maykinmedia/maykin-api-clients/branch/main/graph/badge.svg
    :target: https://codecov.io/gh/maykinmedia/maykin-api-clients
    :alt: Coverage status

.. |docs| image:: https://readthedocs.org/projects/maykin-api-clients/badge/?version=latest
    :target: https://maykin-api-clients.readthedocs.io/en/latest/?badge=latest
    :alt: Documentation Status

.. |python-versions| image:: https://img.shields.io/pypi/pyversions/maykin-api-clients.svg

.. |pypi-version| image:: https://img.shields.io/pypi/v/maykin-api-clients.svg
    :target: https://pypi.org/project/maykin-api-clients/
