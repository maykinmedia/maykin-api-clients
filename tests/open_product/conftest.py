from collections.abc import Iterator

import pytest

from maykin_api_clients.contrib.open_product import OpenProductClient


@pytest.fixture(scope="session")
def op_client() -> Iterator[OpenProductClient]:
    with OpenProductClient(
        base_url="http://localhost:8100",
        token="75167ed1457337f6c27022ae772ba79a351b053a",
    ) as client:
        yield client
