#!/bin/bash

poetry run alembic upgrade head

poetry run uvicorn api.main:app \
    --reload \
    --port $NL_API_PORT \
    --host $NL_API_BIND
