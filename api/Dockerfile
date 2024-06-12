FROM python:3.11.3 AS build

RUN rm /etc/localtime && ln -s /usr/share/zoneinfo/America/Santo_Domingo /etc/localtime

WORKDIR /opt/netolight/api

RUN curl -sSL https://install.python-poetry.org | \
    POETRY_HOME=/usr/local POETRY_VERSION=1.4.0 python -

COPY api .

RUN poetry build

FROM python:3.11.3-slim

RUN rm /etc/localtime && ln -s /usr/share/zoneinfo/America/Santo_Domingo /etc/localtime

WORKDIR /opt/netolight/api

RUN apt-get update && apt-get install net-tools telnet

COPY --from=build /opt/netolight/api/run.sh .
COPY --from=build /opt/netolight/api/alembic.ini .
COPY --from=build /opt/netolight/api/migrations migrations
COPY --from=build /opt/netolight/api/dist/api-*-py3-none-any.whl .

RUN pip install alembic api-*-py3-none-any.whl && rm api-*-py3-none-any.whl

CMD ./run.sh
