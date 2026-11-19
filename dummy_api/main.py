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

from fastapi import FastAPI

app = FastAPI()


@app.get("/camel-case")
def read_camel_case():
    return {
        "apiVersion": "0.1.0",
        "now": datetime.now(tz=UTC),
    }
