from http import HTTPStatus
from typing import ClassVar

import pytest
import requests
from ape_pie import APIClient

from maykin_api_clients.core import (
    BaseResource,
    BaseSchemaStruct,
    ClientIOError,
    ClientResponseError,
    ErrorMap,
    RetrieveOperation,
)
from maykin_api_clients.core.errors import resolve_error_type


class Thing(BaseSchemaStruct):
    name: str


class ErrorBody(BaseSchemaStruct):
    detail: str


class NotFoundBody(BaseSchemaStruct):
    message: str


class ThingResource(BaseResource):
    errors: ClassVar[ErrorMap] = {"default": ErrorBody}

    retrieve = RetrieveOperation(path="things", returns=Thing)


def make_response(status_code: int, content: bytes = b"") -> requests.Response:
    response = requests.Response()
    response.status_code = status_code
    response.reason = HTTPStatus(status_code).phrase
    response.url = "https://example.com/api/things"
    response._content = content
    return response


@pytest.mark.parametrize(
    ("status_code", "expected"),
    [
        (404, "exact"),
        (400, "range"),
        (500, "default"),
    ],
)
def test_resolve_error_type_most_specific_wins(status_code: int, expected: str):
    errors = {404: "exact", "4XX": "range", "default": "default"}

    assert resolve_error_type(errors, status_code) == expected


def test_resolve_error_type_without_match():
    assert resolve_error_type({404: ErrorBody}, 500) is None


def test_success_response_is_decoded():
    response = make_response(200, b'{"name": "foo"}')

    result = ThingResource().process_response(response, struct=Thing)

    assert result == Thing(name="foo")


def test_error_response_raises_with_decoded_body():
    response = make_response(400, b'{"detail": "nope"}')

    with pytest.raises(ClientResponseError) as exc_info:
        ThingResource().process_response(response, struct=Thing)

    exc = exc_info.value
    assert exc.status_code == 400
    assert exc.response is response
    assert exc.body == ErrorBody(detail="nope")
    assert str(exc) == "400 Bad Request for url: https://example.com/api/things"


def test_operation_errors_take_precedence_over_resource_errors():
    response = make_response(404, b'{"message": "gone"}')

    with pytest.raises(ClientResponseError) as exc_info:
        ThingResource().process_response(
            response, struct=Thing, errors={404: NotFoundBody}
        )

    assert exc_info.value.body == NotFoundBody(message="gone")


def test_error_type_can_be_a_union():
    response = make_response(422, b'["field is required"]')

    with pytest.raises(ClientResponseError) as exc_info:
        ThingResource().process_response(
            response, struct=Thing, errors={422: ErrorBody | list[str]}
        )

    assert exc_info.value.body == ["field is required"]


def test_error_body_not_matching_declared_type():
    # e.g. an empty 401 response, while the API declares a JSON error body
    response = make_response(401, b"")

    with pytest.raises(ClientResponseError) as exc_info:
        ThingResource().process_response(response, struct=Thing)

    assert exc_info.value.status_code == 401
    assert exc_info.value.body is None


def test_error_without_declared_type():
    class PlainResource(BaseResource):
        pass

    response = make_response(500, b'{"detail": "boom"}')

    with pytest.raises(ClientResponseError) as exc_info:
        PlainResource().process_response(response, struct=Thing)

    assert exc_info.value.body is None


def test_transport_errors_are_wrapped():
    class Client(APIClient):
        Thing = ThingResource()

    # nothing listens on port 1
    with (
        Client(base_url="http://localhost:1/") as client,
        pytest.raises(ClientIOError) as exc_info,
    ):
        client.Thing.retrieve()

    assert isinstance(exc_info.value.__cause__, requests.ConnectionError)
