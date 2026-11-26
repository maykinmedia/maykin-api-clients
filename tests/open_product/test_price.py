from uuid import UUID

import pytest

from maykin_api_clients.contrib.open_product import OpenProductClient, PriceParams


@pytest.mark.vcr
def test_list_prices(op_client: OpenProductClient):
    response = op_client.Price.list()
    prices = response.results

    assert len(prices) == 2
    assert prices[0].uuid == UUID("d71a7ff5-32e4-4bb8-8293-44728ba60933")
    assert prices[1].uuid == UUID("55ed7060-0f46-4f04-9cb2-8dc494c83a92")


@pytest.mark.vcr
def test_list_prices_with_params(op_client: OpenProductClient):
    response = op_client.Price.list(
        params=PriceParams(producttype__uuid="5d42a943-065a-46e7-8f17-54a5edbc88eb")
    )
    prices = response.results

    assert len(prices) == 1
    assert prices[0].uuid == UUID("55ed7060-0f46-4f04-9cb2-8dc494c83a92")
