VERSION ?= $(shell cat VERSION | cut -d= -f2)
PYTEST ?= pytest
MYPY ?= mypy
DOCKER ?= docker
DOCKER_COMPOSE_ARGS ?=
DOCKER_COMPOSE ?= docker compose
ACR = nldevcr

version:
	echo $(VERSION)

db-revision:
	$(DOCKER_COMPOSE) $(DOCKER_COMPOSE_ARGS) exec $(s) poetry run alembic revision --autogenerate -m "$(c)"

db-upgrade:
	$(DOCKER_COMPOSE) $(DOCKER_COMPOSE_ARGS) exec $(s) poetry run alembic upgrade $(r)

db-downgrade:
	$(DOCKER_COMPOSE) $(DOCKER_COMPOSE_ARGS) exec $(s) poetry run alembic downgrade $(r)

db-history:
	$(DOCKER_COMPOSE) $(DOCKER_COMPOSE_ARGS) exec $(s) poetry run alembic history

db-current-revision:
	$(DOCKER_COMPOSE) $(DOCKER_COMPOSE_ARGS) exec $(s) poetry run alembic current

build:
	$(DOCKER_COMPOSE) $(DOCKER_COMPOSE_ARGS) build $(s)

up:
	$(DOCKER_COMPOSE) $(DOCKER_COMPOSE_ARGS) up -d $(s)

start:
	$(DOCKER_COMPOSE) $(DOCKER_COMPOSE_ARGS) start $(s)

down:
	$(DOCKER_COMPOSE) $(DOCKER_COMPOSE_ARGS) down $(s)

destroy:
	$(DOCKER_COMPOSE) $(DOCKER_COMPOSE_ARGS) down -v $(s)

stop:
	$(DOCKER_COMPOSE) $(DOCKER_COMPOSE_ARGS) stop $(s)

restart:
	$(DOCKER_COMPOSE) $(DOCKER_COMPOSE_ARGS) stop $(s)
	$(DOCKER_COMPOSE) $(DOCKER_COMPOSE_ARGS) up -d $(s)

logs:
	$(DOCKER_COMPOSE) $(DOCKER_COMPOSE_ARGS) logs --tail=100 -f $(s)

ps:
	$(DOCKER_COMPOSE) $(DOCKER_COMPOSE_ARGS) ps

.PHONY: version db-revision db-downgrade db-history db-current-revision build up start down destroy stop restart logs ps
