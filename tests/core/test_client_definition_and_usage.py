"""
Test full request-response processing of a client against the dummy API service.
"""

from __future__ import annotations

from collections.abc import Sequence
from datetime import datetime
from typing import TYPE_CHECKING
from uuid import UUID

import pytest
from ape_pie import APIClient as BaseClient

from maykin_api_clients.core import (
    UNSET,
    BaseResource,
    BaseSchemaStruct,
    CreateOperation,
    ListOperation,
    PayloadArgs,
    QueryArgs,
    QueryParamsStruct,
    RetrieveOperation,
    UnsetType,
)

pytestmark = [pytest.mark.vcr]

#
# Define the client
#


class Todo(BaseSchemaStruct, rename="camel"):
    uuid: UUID
    title: str
    completed_on: datetime | None
    done: bool = False


class TodoParams(QueryParamsStruct, rename="camel"):
    optional_query: str | UnsetType = UNSET


class RetrieveTodoArgs(QueryArgs[TodoParams]):
    uuid: UUID | str


class TodoResource(BaseResource["APIClient"]):
    list = ListOperation(
        path="todos",
        # shorthand for query params without needing a subclass
        call_args=QueryArgs[TodoParams],
        returns=Sequence[Todo],
    )
    retrieve = RetrieveOperation(
        path="todos/{uuid}",
        call_args=RetrieveTodoArgs,
        returns=Todo,
    )
    create = CreateOperation(
        path="todos",
        call_args=PayloadArgs[Todo],
        returns=Todo,
    )


class APIClient(BaseClient):
    Todo = TodoResource()


#
# Tests
#


@pytest.fixture(scope="session")
def api_client():
    with APIClient(base_url="http://localhost:8000") as client:
        yield client


def test_client_resources_interact_with_api(api_client: APIClient):
    todos = api_client.Todo.list()

    assert isinstance(todos, Sequence)
    assert len(todos) >= 2
    assert all(isinstance(x, Todo) for x in todos)

    first_todo = todos[0]
    assert first_todo.uuid == UUID("05442685-15d4-49a6-abd9-2ed0a4bbe73e")
    assert first_todo.title == "Write tests"
    assert first_todo.completed_on is None
    assert first_todo.done is False


def test_client_supports_query_parameters(api_client: APIClient):
    # only specified params are passed along
    todos = api_client.Todo.list(params=TodoParams(optional_query="Write tests"))
    assert len(todos) == 1

    todos_2 = api_client.Todo.list(params=TodoParams())
    assert len(todos_2) >= 2


@pytest.mark.parametrize(
    "uuid",
    [
        "05442685-15d4-49a6-abd9-2ed0a4bbe73e",
        UUID("05442685-15d4-49a6-abd9-2ed0a4bbe73e"),
    ],
)
def test_client_can_use_path_parameters_for_retrieve(
    api_client: APIClient, uuid: str | UUID
):
    todo = api_client.Todo.retrieve(uuid=uuid)

    assert todo.title == "Write tests"
    assert todo.done is False


def test_type_inference(api_client: APIClient):
    retrieve_todo = api_client.Todo.retrieve

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
            params=QueryParamsStruct(),  # pyright: ignore[reportArgumentType]
        )
