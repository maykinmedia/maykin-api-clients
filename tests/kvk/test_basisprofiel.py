"""
Tests against the KvK test environment.

Record cassettes with ``pytest tests/kvk --record-mode=once``.
"""

import pytest

from maykin_api_clients.contrib.kvk import BasisprofielParams, KvKClient
from maykin_api_clients.core import UNSET

from .data import (
    VALID_KVK_NUMMERS,
    WITH_VESTIGINGEN,
    WITHOUT_VESTIGINGEN,
)


@pytest.mark.vcr
@pytest.mark.parametrize("kvk_nummer", VALID_KVK_NUMMERS)
def test_retrieve_basisprofiel(kvk_client: KvKClient, kvk_nummer: str):
    basisprofiel = kvk_client.Basisprofiel.retrieve(kvk_nummer=kvk_nummer)

    assert basisprofiel.kvk_nummer == kvk_nummer
    assert basisprofiel.embedded is not UNSET
    assert basisprofiel.embedded.eigenaar is not UNSET


@pytest.mark.vcr
@pytest.mark.parametrize("kvk_nummer", VALID_KVK_NUMMERS)
def test_retrieve_eigenaar(kvk_client: KvKClient, kvk_nummer: str):
    eigenaar = kvk_client.Basisprofiel.eigenaar(kvk_nummer=kvk_nummer)

    assert eigenaar.rechtsvorm is not UNSET


@pytest.mark.vcr
@pytest.mark.parametrize("kvk_nummer", WITH_VESTIGINGEN)
def test_retrieve_hoofdvestiging(kvk_client: KvKClient, kvk_nummer: str):
    hoofdvestiging = kvk_client.Basisprofiel.hoofdvestiging(kvk_nummer=kvk_nummer)

    assert hoofdvestiging.kvk_nummer == kvk_nummer
    assert hoofdvestiging.ind_hoofdvestiging == "Ja"


@pytest.mark.vcr
@pytest.mark.parametrize("kvk_nummer", WITH_VESTIGINGEN)
def test_list_vestigingen(kvk_client: KvKClient, kvk_nummer: str):
    vestiging_list = kvk_client.Basisprofiel.vestigingen(kvk_nummer=kvk_nummer)

    assert vestiging_list.kvk_nummer == kvk_nummer
    assert vestiging_list.vestigingen is not UNSET
    assert len(vestiging_list.vestigingen) == vestiging_list.totaal_aantal_vestigingen


@pytest.mark.vcr
@pytest.mark.parametrize("kvk_nummer", WITHOUT_VESTIGINGEN)
def test_list_vestigingen_without_vestigingen(kvk_client: KvKClient, kvk_nummer: str):
    vestiging_list = kvk_client.Basisprofiel.vestigingen(kvk_nummer=kvk_nummer)

    assert vestiging_list.kvk_nummer == kvk_nummer
    assert vestiging_list.totaal_aantal_vestigingen == 0
    # the key is omitted rather than an empty list
    assert vestiging_list.vestigingen is UNSET


@pytest.mark.vcr
def test_retrieve_basisprofiel_with_geo_data(kvk_client: KvKClient):
    basisprofiel = kvk_client.Basisprofiel.retrieve(
        kvk_nummer="68750110",
        params=BasisprofielParams(geo_data=True),
    )

    assert basisprofiel.embedded is not UNSET
    hoofdvestiging = basisprofiel.embedded.hoofdvestiging
    assert hoofdvestiging is not UNSET
    assert hoofdvestiging.adressen is not UNSET
    assert hoofdvestiging.adressen[0].geo_data is not UNSET


def test_geo_data_param_serialized_as_json_boolean():
    assert BasisprofielParams(geo_data=True).as_params() == {"geoData": "true"}
    assert BasisprofielParams().as_params() == {}
