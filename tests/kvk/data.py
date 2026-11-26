"""
Test set of the KvK test environment, see https://developers.kvk.nl/documentation/testing

The test ids double as cassette names.
"""

import pytest

from maykin_api_clients.contrib.kvk.common import ErrorResponseBody, Fout

# registrations with an onderneming, and thus at least a hoofdvestiging
WITH_VESTIGINGEN = [
    pytest.param("69599084", id="eenmanszaak-69599084"),
    pytest.param("68727720", id="nv-68727720"),
    pytest.param("68750110", id="bv-68750110"),
    pytest.param("90001354", id="bv-90001354"),
    pytest.param("90006623", id="stichting-90006623"),
    pytest.param("69599076", id="vof-69599076"),
    pytest.param("90005414", id="vof-90005414"),
    pytest.param("96354429", id="cooperatie-inactief-96354429"),
    pytest.param("90002490", id="owm-90002490"),
    pytest.param("90001745", id="maatschap-90001745"),
    pytest.param("90003942", id="cv-90003942"),
]

# Rechtspersonen without an onderneming have no vestigingen: the ``vestigingen`` key is
# omitted from the vestigingen list and the hoofdvestiging endpoint responds with 404.
WITHOUT_VESTIGINGEN = [
    pytest.param("90004760", id="nv-90004760"),
    pytest.param("69599068", id="stichting-69599068"),
    pytest.param("90000102", id="stichting-90000102"),
    pytest.param("90002520", id="kerkgenootschap-90002520"),
    pytest.param("90000749", id="vve-90000749"),
    pytest.param("55505201", id="overige-privaatrechtelijke-rp-55505201"),
]

VALID_KVK_NUMMERS = WITH_VESTIGINGEN + WITHOUT_VESTIGINGEN

# documented to return an error message
ERROR_KVK_NUMMERS = [
    pytest.param("90004973", id="error-90004973"),
    pytest.param("90002903", id="error-90002903"),
]


def not_deliverable_error_factory(kvk_nummer: str) -> ErrorResponseBody:
    """
    The error body the test environment returns for all documented error cases.

    Also returned by the hoofdvestiging endpoint for registrations without vestigingen.
    """
    omschrijving = (
        f"Op basis van het KVK-nummer {kvk_nummer} kan het product niet worden "
        "geleverd."
    )
    return ErrorResponseBody(fout=[Fout(code="IPD0005", omschrijving=omschrijving)])
