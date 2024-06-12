FROM python:3.11.3 AS build

WORKDIR /opt/netolight/dimmer

RUN curl -sSL https://install.python-poetry.org | \
    POETRY_HOME=/usr/local POETRY_VERSION=1.4.0 python -

COPY dimmer .

RUN poetry build

CMD /bin/bash

FROM python:3.11.3-slim

RUN apt-get update \
    && apt-get -y install libpq-dev gcc \
    && pip install psycopg2

COPY --from=build /opt/netolight/dimmer/dist/dimmer-*-py3-none-any.whl .

CMD /bin/bash

RUN pip install dimmer-*-py3-none-any.whl

RUN rm dimmer-*-py3-none-any.whl

CMD python -m dimmer.main
