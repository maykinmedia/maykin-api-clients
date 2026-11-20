"""
Test full request-response processing of a client against the dummy API service.
"""

from __future__ import annotations

from collections.abc import Sequence
from datetime import UTC, datetime
from typing import TYPE_CHECKING, Annotated
from uuid import UUID

import msgspec
import pytest
from ape_pie import APIClient

from maykin_api_clients.core import (
    UNSET,
    BaseResource,
    BaseSchemaStruct,
    ListOperation,
    QueryArgs,
    QueryParamsStruct,
    RetrieveOperation,
    UnsetType,
)

pytestmark = [pytest.mark.vcr]


class BaseSchema(BaseSchemaStruct, rename="camel"):
    pass


class BaseParams(QueryParamsStruct, rename="camel"):
    pass


class Meta(BaseSchema):
    api_version: Annotated[str, msgspec.Meta(pattern=r"\d+\.\d+\.\d")]
    now: datetime
    query: str = ""


class Todo(BaseSchema):
    title: str
    done: bool = False


class MetaParams(BaseParams):
    optional_query: str | UnsetType = UNSET


class MetaArgs(QueryArgs[MetaParams]):
    pass


class MetaResource(BaseResource["DummyAPIClient"]):
    retrieve = RetrieveOperation(
        path="camel-case",
        call_args=MetaArgs,
        returns=Meta,
    )


class TodoParams(BaseParams):
    optional_query: str | UnsetType = UNSET


class ListTodoArgs(QueryArgs[TodoParams]):
    pass


class RetrieveTodoArgs(QueryArgs[TodoParams]):
    uuid: UUID | str


class TodoResource(BaseResource["DummyAPIClient"]):
    list = ListOperation(
        path="todos",
        call_args=ListTodoArgs,
        returns=Sequence[Todo],
    )
    retrieve = RetrieveOperation(
        path="todos/{uuid}",
        call_args=RetrieveTodoArgs,
        returns=Todo,
    )


class DummyAPIClient(APIClient):
    meta = MetaResource()
    todo = TodoResource()


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


@pytest.mark.parametrize(
    "uuid",
    [
        "a4cc47ba-cab1-4189-a58c-189a3d29d412",
        UUID("a4cc47ba-cab1-4189-a58c-189a3d29d412"),
    ],
)
def test_client_can_use_path_parameters_for_retrieve(
    dummy_api_client: DummyAPIClient,
    uuid: str | UUID,
):
    todo = dummy_api_client.todo.retrieve(uuid=uuid)

    assert todo.title == "Write tests"
    assert todo.done is False


def test_type_inference(dummy_api_client: DummyAPIClient):
    retrieve_todo = dummy_api_client.todo.retrieve

    if TYPE_CHECKING:
        # valid calls
        retrieve_todo(uuid="a4cc47ba-cab1-4189-a58c-189a3d29d412")
        retrieve_todo(uuid=UUID("a4cc47ba-cab1-4189-a58c-189a3d29d412"))
        retrieve_todo(uuid="a4cc47ba-cab1-4189-a58c-189a3d29d412", params=None)
        retrieve_todo(
            uuid="a4cc47ba-cab1-4189-a58c-189a3d29d412",
            params=TodoParams(optional_query="query"),
        )

        # invalid calls - if the reportCallIssue is not raised,
        # reportUnnecessaryTypeIgnoreComment (see pyproject.toml) will report an error
        retrieve_todo(pk=3)  # pyright: ignore[reportCallIssue]
        retrieve_todo(uuid=3)  # pyright: ignore[reportArgumentType]
        retrieve_todo(
            uuid="a4cc47ba-cab1-4189-a58c-189a3d29d412",
            params=MetaParams(optional_query="query"),  # pyright: ignore[reportArgumentType]
        )


def test_list_operation_returns_list_of_todos(dummy_api_client: DummyAPIClient):
    todos = dummy_api_client.todo.list()

    assert len(todos) == 2
    assert all(isinstance(todo, Todo) for todo in todos)


def test_list_operation_supports_query_params(dummy_api_client: DummyAPIClient):
    todos = dummy_api_client.todo.list(params=TodoParams(optional_query="hi"))

    assert len(todos) == 2
