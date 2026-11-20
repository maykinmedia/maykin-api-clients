.. _reference_operations:

===========================
Generic resource operations
===========================

A resource `operation <https://swagger.io/docs/specification/v3_0/paths-and-operations/#operations>`_
is the combination of a particular API endpoint with a particular HTTP method. There are
common patterns that most (RESTful or REST-inspired) APIs provide:

* list: ``GET`` on a collection endpoint
* retrieve: ``GET`` on a detail endpoint
* create: ``POST`` on a collection endpoint
* update: ``PUT`` on a detail endpoint
* partial update: ``PATCH`` on a detail endpoint
* destroy: ``DELETE`` on a detail endpoint

The core of this library provides declarative classes for these common operations that
cut down on boiler plate.

Example usage
=============

The sample below configures an API client that allows looking up a single "Todo" from
an API.


.. code-block:: python

    from datetime import datetime

    from ape_pie import APIClient
    from maykin_api_clients.core import (
        Args,
        BaseResource,
        BaseSchemaStruct,
        RetrieveOperation,
    )


    class Todo(BaseSchemaStruct):  # struct for the return value
        name: str
        completed_on: datetime | None


    class TodoDetailArgs(Args):  # type definitions of path parameters
        id: int


    class TodoResource(BaseResource["TodoClient"]):
        retrieve = RetrieveOperation(
            path="todos/{id}", call_args=TodoDetailArgs, returns=Todo
        )


    class TodoClient(APIClient):
        Todo = TodoResource()


    if __name__ == "__main__":
        client = TodoClient(base_url="http://localhost:8000")
        todo = client.Todo.retrieve(id=42)
        assert isinstance(todo, Todo)


Some things are worth pointing out:

1. The ``call_args`` makes the ``.retrieve(...)`` call strongly typed and provides
   editor autocomplete.
2. The path parameters provided through ``.retrieve(...)`` are automatically
   interpolated in the configured ``path`` of the operation.
3. The ``returns`` parameter dictates the return value of ``.retrieve(...)``, and is
   used under the hood to validate the response data with msgspec.

Built-in operations
===================

.. autoclass:: maykin_api_clients.core.RetrieveOperation
    :members:

Custom operations
=================

...
