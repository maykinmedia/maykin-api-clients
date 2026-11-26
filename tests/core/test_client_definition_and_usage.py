"""
Test full request-response processing of a client against the dummy API service.
"""

from __future__ import annotations

from collections.abc import Sequence
from datetime import datetime
from typing import TYPE_CHECKING, Generic, assert_type
from uuid import UUID

import pytest
from ape_pie import APIClient as BaseClient
from typing_extensions import TypeVar

from maykin_api_clients.core import (
    UNSET,
    BaseResource,
    BaseSchemaStruct,
    UnsetType,
)
from maykin_api_clients.core.operations import as_json, as_params, operation

pytestmark = [pytest.mark.vcr]

#
# Define the client
#


class ToDo(BaseSchemaStruct, rename="camel"):
    uuid: UUID
    title: str
    completed_on: datetime | None
    done: bool = False


class TodoParams(BaseSchemaStruct, rename="camel"):
    optional_query: str | UnsetType = UNSET


TD = TypeVar("TD", bound=ToDo, default=ToDo)
"""
The ToDo struct of a resource, which API dialects can replace with a subclass.
"""


class TodoResource(BaseResource["APIClient"], Generic[TD]):
    def __init__(self, todo: type[TD] = ToDo) -> None:
        self.todo = todo

    @operation("todos")
    def list(self, url_path: str, /, params: TodoParams | None = None):
        """
        Get the collection of todos from the API.
        """
        return (
            self.http_client.get(url_path, params=as_params(params)),
            Sequence[self.todo],
        )

    @operation("todos/{uuid}")
    def retrieve(
        self, url_path: str, /, uuid: UUID | str, params: TodoParams | None = None
    ):
        return (self.http_client.get(url_path, params=as_params(params)), self.todo)

    @operation("todos")
    def create(self, url_path: str, /, payload: ToDo):
        return (
            self.http_client.post(url_path, json=as_json(payload)),
            self.todo,
        )


class APIClient(BaseClient):
    ToDo = TodoResource()


class _MyToDo(ToDo):
    optional_arg: str = "default"


class CustomClient(APIClient):
    ToDo = TodoResource(todo=_MyToDo)


#
# Tests
#


@pytest.fixture(scope="session")
def api_client():
    with APIClient(base_url="http://localhost:8000") as client:
        yield client


def test_client_resources_interact_with_api(api_client: APIClient):
    todos = api_client.ToDo.list()

    assert isinstance(todos, Sequence)
    assert len(todos) >= 2
    assert all(isinstance(x, ToDo) for x in todos)

    first_todo = todos[0]
    assert first_todo.uuid == UUID("05442685-15d4-49a6-abd9-2ed0a4bbe73e")
    assert first_todo.title == "Write tests"
    assert first_todo.completed_on is None
    assert first_todo.done is False


def test_client_supports_query_parameters(api_client: APIClient):
    # only specified params are passed along
    todos = api_client.ToDo.list(params=TodoParams(optional_query="Write tests"))
    assert len(todos) == 1

    todos_2 = api_client.ToDo.list(params=TodoParams())
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
    todo = api_client.ToDo.retrieve(uuid=uuid)

    assert_type(todo, ToDo)
    assert todo.title == "Write tests"
    assert todo.done is False


def test_type_inference(api_client: APIClient):
    retrieve_todo = api_client.ToDo.retrieve

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
            params=BaseSchemaStruct(),  # pyright: ignore[reportArgumentType]
        )


def test_custom_return_type_struct(api_client: APIClient):
    class CustomToDo(BaseSchemaStruct):
        title: str
        imaginary_attribute: str = "I do not exist"

    todo = api_client.ToDo.retrieve.returning(CustomToDo)(
        uuid="05442685-15d4-49a6-abd9-2ed0a4bbe73e"
    )

    assert_type(todo, CustomToDo)
    assert isinstance(todo, CustomToDo)
    assert todo.title == "Write tests"
    assert not hasattr(todo, "done")
    assert todo.imaginary_attribute == "I do not exist"


def test_client_resource_customization():
    with CustomClient(base_url="http://localhost:8000") as client:
        todos = client.ToDo.list()
        todo = client.ToDo.retrieve(uuid="05442685-15d4-49a6-abd9-2ed0a4bbe73e")

    assert_type(todos, Sequence[_MyToDo])
    assert len(todos) >= 2
    assert all(isinstance(x, _MyToDo) for x in todos)
    assert_type(todo, _MyToDo)
    assert isinstance(todo, _MyToDo)
    assert todo.optional_arg == "default"
