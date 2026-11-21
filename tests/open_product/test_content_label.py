import pytest

from maykin_api_clients.contrib.open_product import OpenProductClient


@pytest.mark.vcr
def test_list_content_labels(op_client: OpenProductClient):
    response = op_client.ContentLabel.list()
    content_labels = response.results

    assert len(content_labels) == 2
    assert content_labels[0].naam == "Voorwaarden"
    assert content_labels[1].naam == "Eisen"
