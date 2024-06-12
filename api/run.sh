#!/bin/bash

alembic upgrade head

gunicorn \
    --worker-class=uvicorn.workers.UvicornWorker \
    --bind=$NL_API_BIND:$NL_API_PORT \
    api.main:app
