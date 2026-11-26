"""
Dummy API for the core tests.

The service is implemented as a simple Fast API service. You can run this in local
development mode, or use the docker compose from the root of the repo. This service is
intentionally simplistic for ease of debugging.

Run in dev using:

.. code-block:: bash

    fastapi dev dummy_api/main.py

"""

from datetime import UTC, datetime
from typing import Annotated
from uuid import UUID

from fastapi import FastAPI, HTTPException, Query

app = FastAPI()


TODOS = [
    {
        "uuid": UUID("05442685-15d4-49a6-abd9-2ed0a4bbe73e"),
        "title": "Write tests",
        "done": False,
        "completedOn": None,
    },
    {
        "uuid": UUID("d19ea23e-cfa2-4e16-9ad0-200bd85d1098"),
        "title": "Think about architecture",
        "done": True,
        "completedOn": datetime(2026, 11, 23, 18, 0, 5, tzinfo=UTC),
    },
]


@app.get("/todos")
def list_todos(
    optional_query: Annotated[str, Query(alias="optionalQuery")] = "",
):
    return [
        todo
        for todo in TODOS
        if (not optional_query or optional_query in todo["title"])
    ]


@app.get("/todos/{uuid}")
def read_todo(
    uuid: UUID,
    optional_query: Annotated[str, Query(alias="optionalQuery")] = "",
):
    todo = next((todo for todo in TODOS if todo["uuid"] == uuid), None)
    if todo is None:
        raise HTTPException(status_code=404, detail="Not found.")
    return todo
