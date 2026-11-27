.. _reference_clients:

===========
API clients
===========

Ready-to-use API clients are the selling point of Maykin's API clients library -
downstream projects only have to import them and start using them (optionally some
configuration may be desired).

These clients need to be built before you can use them. How you do that is laid out on
this page.

The sections build upon the results of the preceding section. For the "API" we assume
a simple JSON API for "Todos" with the following endpoints:

* A Todo has a string ``name``, ISO-8601 datetime ``completedOn`` (or ``null``), and an
  integer ``id``.
* ``GET /todos`` returns an unpaginated list of Todos.
* ``POST /todos`` creates a new Todo, requiring only the ``name`` property.
* ``GET /todos/:id`` looks up a single Todo, returning all its properties.

Building a Todo client that can list Todos
==========================================

To start out simple, we implement a client that can list and retrieve Todo's from the
API.

Client basis
------------

The actual client class can use any transport as base that implements the
:class:`requests.Session` interface. For Maykin, we typically use
:class:`ape_pie.APIClient` as it contains some hardening and convenience implementation
details:

.. code-block:: python

    from ape_pie import APIClient


    class TodoClient(APIClient):
        pass


This client by itself is of course pretty useless - you can instantiate it and call
requests methods through it, but that's quite limited to what we actually want to
provide.

.. code-block:: python

    with TodoClient(base_url="http://localhost:8000") as client:
        response = client.get("todos/42")

        assert response.status_code == 200
        assert isinstance(response.json(), dict)

Defining structs for the expected data
--------------------------------------

maykin-api-clients is (initially) build on top of :class:`msgspec.Struct` - they
validate the JSON data at the boundary and transform it into native Python types so
that you're working with rich Python objects inside your client/project.

We model the Todo API resource shape:

.. code-block:: python

    from maykin_api_clients.core import BaseSchemaStruct

    class Todo(BaseSchemaStruct, rename="camel"):
        id: int
        name: str
        completed_on: datetime | None

These 4 lines of code do a lot of work already!

* the ``rename="camel"`` will transform the API's camel case JSON into idomatic Python
  snake case: "completedOn" gets translated to "completed_on".
* the ``completed_on`` declaration will automatically translate the datetime strings
  into python ``datetime`` instances, and if the response contains ``null`` instead
  because the Todo is not yet complete, then our ``Todo`` instance will have
  ``todo.completed_on`` set to ``None`` instead.
* msgspec will raise validation errors if the input data does not match the declared
  schema. And, it will (by default) ignore additional data that's unused.

Defining the API client resource
--------------------------------

An API client resource is centered around the entity/resource upon which operations are
executed in the API, such as retrieving, getting a list, creating, updating... Here
we're interested in the "retrieve" and "list" operations of the Todo resource, so let's
go ahead and define the list operation:

.. code-block:: python

    from collections.abc import Sequence

    from maykin_api_clients.core import BaseResource, ListOperation


    class TodoResource(BaseResource):
        list = ListOperation(path="todos", returns=Sequence[Todo])


``ListOperation`` is one of the :ref:`generic operations <reference_operations>` that
removes boilerplate for common operations.

* ``path`` specifies the relative endpoint to call, with the HTTP ``GET`` method.
* ``returns`` specifies the expected shape of the JSON response data.

Here a plain, unpaginated list response is expected.

Wiring up the resource to the client
------------------------------------

To expose the resource via the client, it needs to be declared on the client:

.. code-block:: python

    class TodoClient(APIClient):
        Todo = TodoResource()


This enables you to get a list of all Todos:

.. code-block:: python

    with TodoClient(base_url="http://localhost:8000") as client:
        todos = client.Todo.list()

        assert isinstance(todos, Sequence)
        assert len(todos) >= 1

        todo = todos[0]
        assert isinstance(todo, Todo)
        assert isinstance(todo.id, int)
        assert isinstance(todo.name, str)
        assert isinstance(todo.completed_on, datetime | None)


Supporting detail operations with path parameters
=================================================

...


Supporting query parameters
===========================

...
