import os
from collections.abc import Iterator

import pytest

from maykin_api_clients.contrib.kvk import KVK_TEST_URL, KvKClient


@pytest.fixture(scope="session")
def vcr_config(vcr_config):
    return {
        **vcr_config,
        "filter_headers": [*vcr_config["filter_headers"], "apikey"],
    }


@pytest.fixture(scope="session")
def kvk_client() -> Iterator[KvKClient]:
    # Publicly documented API key for the KvK test environment, only used when
    # (re-)recording cassettes. It's filtered out of the cassettes.
    with KvKClient(
        base_url=KVK_TEST_URL,
        api_key=os.environ.get(
            "KVK_TEST_API_KEY", "l7xx1f2691f2520d487b902f4e0b57a0b197"
        ),
    ) as client:
        yield client
