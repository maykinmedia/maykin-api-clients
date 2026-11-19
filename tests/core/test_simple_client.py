"""
Test full request-response processing of a client against the dummy API service.
"""

from __future__ import annotations

from datetime import UTC, datetime
from typing import Annotated

import msgspec
import pytest
from ape_pie import APIClient

from maykin_api_clients.core.query_params import QueryParamsStruct
from maykin_api_clients.core.resources import BaseResource
from maykin_api_clients.core.structs import BaseSchemaStruct


class BaseSchema(BaseSchemaStruct, rename="camel"):
    pass


class BaseParams(QueryParamsStruct, rename="camel"):
    pass


class Meta(BaseSchema):
    api_version: Annotated[str, msgspec.Meta(pattern=r"\d+\.\d+\.\d")]
    now: datetime
    query: str = ""


class MetaParams(BaseParams):
    optional_query: str | msgspec.UnsetType = msgspec.UNSET


class MetaResource(BaseResource["DummyAPIClient"]):
    def retrieve(self, *, params: MetaParams | None = None) -> Meta:
        response = self._get("camel-case", params=params)
        return self.process_response(response, struct=Meta)


class DummyAPIClient(APIClient):
    meta = MetaResource()


@pytest.fixture(scope="session")
def dummy_api_client():
    with DummyAPIClient(base_url="http://localhost:8000") as client:
        yield client


def test_client_can_use_resources_to_call_an_api_endpoint(
    dummy_api_client: DummyAPIClient,
):
    data = dummy_api_client.meta.retrieve()

    assert isinstance(data, Meta)
    assert data.api_version == "0.1.0"
    assert isinstance(data.now, datetime)
    assert data.now.tzinfo == UTC


def test_client_supports_query_parameters(
    dummy_api_client: DummyAPIClient,
):
    data = dummy_api_client.meta.retrieve(
        params=MetaParams(optional_query="Hello world")
    )

    assert data.query == "Hello world"
