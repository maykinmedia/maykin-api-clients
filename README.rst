Maykin's API clients
====================

:Source: https://github.com/maykinmedia/maykin-api-clients
:Keywords: Common Ground, API clients, JSON APIs

Feature-complete clients for APIs in the Dutch government API landscape.

|build-status| |code-quality| |ruff| |coverage| |docs|

|python-versions| |pypi-version|

About
=====

Maykin's API clients is a python package providing API client implementations for
(JSON-based) APIs commonly encountered in the
`Common Ground <https://commonground.nl/>`_ / (local) Dutch government data landscape.

Clients share an architectural foundation that enables a good DX for projects using the
clients, focusing on type safety, correctness and avoiding re-inventing the wheel every
time in every project.

Planned clients
---------------

* ZGW APIs (Zaken API, Documenten API, Catalogi API, Besluiten API)
* Open Product
* Open Klant
* Open Object
* Haal Centraal BRP Personen bevragen
* BRK
* KvK

If a particular API is not in this list, open a feature request and/or add it yourself!

Installation and usage
======================

See the `docs <https://maykin-api-clients.readthedocs.io/>`_.

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
