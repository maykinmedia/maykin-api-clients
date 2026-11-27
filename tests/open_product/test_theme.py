from uuid import UUID

import pytest

from maykin_api_clients.contrib.open_product import OpenProductClient, ThemeParams


@pytest.mark.vcr
def test_list_themes(op_client: OpenProductClient):
    response = op_client.Theme.list()
    themes = response.results

    assert len(themes) == 3
    assert themes[0].uuid == UUID("619b8102-c476-4c38-af10-990990e6cf8f")
    assert themes[1].uuid == UUID("ce3132cc-1c8f-4476-9ea6-1ff93e0ea9e4")
    assert themes[2].uuid == UUID("cfac32d8-9ced-4b90-aa5c-46ea1cbfe04f")


@pytest.mark.vcr
def test_list_themes_with_params(op_client: OpenProductClient):
    response = op_client.Theme.list(
        params=ThemeParams(producttypen__uuid="9903945d-b639-49da-85ed-7305817f47ad")
    )
    themes = response.results

    assert len(themes) == 1
    assert themes[0].uuid == UUID("ce3132cc-1c8f-4476-9ea6-1ff93e0ea9e4")
