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

from fastapi import FastAPI, Query

app = FastAPI()


@app.get("/camel-case")
def read_camel_case(
    optional_query: Annotated[str, Query(alias="optionalQuery")] = "",
):
    return {
        "apiVersion": "0.1.0",
        "now": datetime.now(tz=UTC),
        "query": optional_query,
    }


@app.get("/todos/{uuid}")
def read_todo(uuid: UUID):
    return {
        "uuid": uuid,
        "title": "Write tests",
        "done": False,
    }
