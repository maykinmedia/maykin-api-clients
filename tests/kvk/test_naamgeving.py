"""
Tests against the KvK test environment.

Record cassettes with ``pytest tests/kvk --record-mode=once``.
"""

import pytest

from maykin_api_clients.contrib.kvk import KvKClient
from maykin_api_clients.core import UNSET

from .data import VALID_KVK_NUMMERS

KVK_NUMMER = "68750110"


@pytest.mark.vcr
def test_retrieve_naamgeving(kvk_client: KvKClient):
    naamgeving = kvk_client.Naamgeving.retrieve(kvk_nummer=KVK_NUMMER)

    assert naamgeving.kvk_nummer == KVK_NUMMER
    assert naamgeving.naam == "Test BV Donald"
    assert naamgeving.startdatum == "20170519"
    assert naamgeving.links is not UNSET
    links = {link.rel: link.href for link in naamgeving.links}
    assert links["basisprofiel"] == (
        f"https://api.kvk.nl/test/api/v1/basisprofielen/{KVK_NUMMER}"
    )
    assert naamgeving.vestigingen is not UNSET
    assert {v.vestigingsnummer for v in naamgeving.vestigingen} == {
        "000037178598",
        "000037178601",
    }
    # both are commerciële vestigingen
    assert all(v.eerste_handelsnaam is not UNSET for v in naamgeving.vestigingen)


@pytest.mark.vcr
@pytest.mark.parametrize("kvk_nummer", VALID_KVK_NUMMERS)
def test_retrieve_naamgeving_for_legal_form(kvk_client: KvKClient, kvk_nummer: str):
    naamgeving = kvk_client.Naamgeving.retrieve(kvk_nummer=kvk_nummer)

    assert naamgeving.kvk_nummer == kvk_nummer
    for vestiging in naamgeving.vestigingen or []:
        # either a commerciële or a niet-commerciële vestiging
        assert (vestiging.eerste_handelsnaam is not UNSET) or (
            vestiging.naam is not UNSET
        )
