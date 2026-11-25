"""
Tests against the KvK test environment.

Record cassettes with ``pytest tests/kvk --record-mode=once``.
"""

import pytest

from maykin_api_clients.contrib.kvk import KvKClient, VestigingsprofielParams
from maykin_api_clients.core import UNSET

from .data import WITH_VESTIGINGEN

# vestigingen of KvK test company 68750110 (see the Basisprofiel cassettes)
HOOFDVESTIGING = "000037178598"
NEVENVESTIGING = "000037178601"


@pytest.mark.vcr
@pytest.mark.parametrize("kvk_nummer", WITH_VESTIGINGEN)
def test_retrieve_all_vestigingen_for_legal_form(
    kvk_client: KvKClient, kvk_nummer: str
):
    # the test set only lists KvK numbers, so look up the vestigingsnummers first
    vestiging_list = kvk_client.Basisprofiel.vestigingen(kvk_nummer=kvk_nummer)
    assert vestiging_list.vestigingen is not UNSET

    for basis in vestiging_list.vestigingen:
        assert basis.vestigingsnummer is not UNSET
        vestiging = kvk_client.Vestigingsprofiel.retrieve(
            vestigingsnummer=basis.vestigingsnummer
        )

        assert vestiging.vestigingsnummer == basis.vestigingsnummer
        assert vestiging.kvk_nummer == kvk_nummer
        assert vestiging.ind_hoofdvestiging == basis.ind_hoofdvestiging


@pytest.mark.vcr
def test_retrieve_hoofdvestiging(kvk_client: KvKClient):
    vestiging = kvk_client.Vestigingsprofiel.retrieve(vestigingsnummer=HOOFDVESTIGING)

    assert vestiging.vestigingsnummer == HOOFDVESTIGING
    assert vestiging.kvk_nummer == "68750110"
    assert vestiging.ind_hoofdvestiging == "Ja"


@pytest.mark.vcr
def test_retrieve_nevenvestiging(kvk_client: KvKClient):
    vestiging = kvk_client.Vestigingsprofiel.retrieve(vestigingsnummer=NEVENVESTIGING)

    assert vestiging.vestigingsnummer == NEVENVESTIGING
    assert vestiging.ind_hoofdvestiging == "Nee"


@pytest.mark.vcr
def test_retrieve_with_geo_data(kvk_client: KvKClient):
    vestiging = kvk_client.Vestigingsprofiel.retrieve(
        vestigingsnummer=HOOFDVESTIGING,
        params=VestigingsprofielParams(geo_data=True),
    )

    assert vestiging.adressen is not UNSET
    assert any(adres.geo_data is not UNSET for adres in vestiging.adressen)
