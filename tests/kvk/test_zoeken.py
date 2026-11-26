"""
Tests against the KvK test environment.

Record cassettes with ``pytest tests/kvk --record-mode=once`` and tighten the
assertions with the recorded data.
"""

import pytest

from maykin_api_clients.contrib.kvk import (
    KvKClient,
    ZoekenParams,
    ZoekenPostcodeHuisnummerParams,
    ZoekenPostcodePostbusParams,
)
from maykin_api_clients.core import UNSET

from .data import VALID_KVK_NUMMERS


@pytest.mark.vcr
@pytest.mark.parametrize("kvk_nummer", VALID_KVK_NUMMERS)
def test_search_by_kvk_nummer_for_legal_form(kvk_client: KvKClient, kvk_nummer: str):
    resultaat = kvk_client.Zoeken.list(
        params=ZoekenParams(
            kvk_nummer=kvk_nummer,
            # the test set contains an inactive registration
            inclusief_inactieve_registraties=True,
        )
    )

    assert resultaat.resultaten is not UNSET
    assert resultaat.resultaten
    assert {item.kvk_nummer for item in resultaat.resultaten} == {kvk_nummer}


@pytest.mark.vcr
def test_search_by_name(kvk_client: KvKClient):
    resultaat = kvk_client.Zoeken.list(params=ZoekenParams(naam="test"))

    assert resultaat.totaal is not UNSET
    assert resultaat.totaal > 0
    assert resultaat.resultaten is not UNSET
    assert resultaat.resultaten


@pytest.mark.vcr
def test_search_by_kvk_nummer_and_type(kvk_client: KvKClient):
    resultaat = kvk_client.Zoeken.list(
        params=ZoekenParams(kvk_nummer="68750110", type=["hoofdvestiging"])
    )

    assert resultaat.resultaten is not UNSET
    assert {item.kvk_nummer for item in resultaat.resultaten} == {"68750110"}
    assert {item.type for item in resultaat.resultaten} == {"hoofdvestiging"}


@pytest.mark.vcr
def test_search_pagination(kvk_client: KvKClient):
    resultaat = kvk_client.Zoeken.list(
        params=ZoekenParams(naam="test", pagina=2, resultaten_per_pagina=5)
    )

    assert resultaat.pagina == 2
    assert resultaat.resultaten_per_pagina == 5
    assert resultaat.resultaten is not UNSET
    assert len(resultaat.resultaten) <= 5


def test_params_serialization():
    params = ZoekenParams(
        naam="test",
        type=["hoofdvestiging", "rechtspersoon"],
        inclusief_inactieve_registraties=True,
        resultaten_per_pagina=50,
    )

    assert params.as_params() == {
        "naam": "test",
        "type": ["hoofdvestiging", "rechtspersoon"],
        "inclusiefInactieveRegistraties": "true",
        "resultatenPerPagina": 50,
    }


def test_postcode_huisnummer_params_serialization():
    params = ZoekenPostcodeHuisnummerParams(
        postcode="3511BT",
        huisnummer=300,
        huisletter="D",
        type=["hoofdvestiging"],
    )

    assert params.as_params() == {
        "postcode": "3511BT",
        "huisnummer": 300,
        "huisletter": "D",
        "type": ["hoofdvestiging"],
    }


def test_postcode_postbus_params_serialization():
    params = ZoekenPostcodePostbusParams(postcode="3511BT", postbusnummer=9292)

    assert params.as_params() == {"postcode": "3511BT", "postbusnummer": 9292}


# The ``pyright: ignore`` comments double as static assertions: the project config
# reports unnecessary ignores as errors, so these lines must remain type errors.


def test_postcode_requires_huisnummer_or_postbusnummer():
    with pytest.raises(TypeError):
        ZoekenParams(postcode="3511BT")  # pyright: ignore[reportCallIssue]


def test_huisnummer_requires_postcode():
    with pytest.raises(TypeError):
        ZoekenPostcodeHuisnummerParams(huisnummer=300)  # pyright: ignore[reportCallIssue]


def test_huisletter_requires_huisnummer():
    with pytest.raises(TypeError):
        ZoekenPostcodePostbusParams(
            postcode="3511BT",
            postbusnummer=9292,
            huisletter="D",  # pyright: ignore[reportCallIssue]
        )
