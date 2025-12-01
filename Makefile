.DEFAULT_GOAL := up

ENV_FILE = .env

export ENV_FILE

# Dev
up_fg:
	make -f scripts/docker_app_makefile up_fg
up:
	make -f scripts/docker_app_makefile up
build:
	make -f scripts/docker_app_makefile build
down:
	make -f scripts/docker_app_makefile down

# Prod
prod_up_fg:
	make -f scripts/docker_app_makefile prod_up_fg
prod_up:
	make -f scripts/docker_app_makefile prod_up
prod_build:
	make -f scripts/docker_app_makefile prod_build
prod_down:
	make -f scripts/docker_app_makefile prod_down

# Tools
logs:
	make -f scripts/docker_app_makefile logs
test:
	make -f scripts/docker_app_makefile test
migrate:
	make -f scripts/docker_app_makefile migrate
downgrade:
	make -f scripts/docker_app_makefile downgrade
migration_create:
	make -f scripts/docker_app_makefile migration_create MESSAGE="$(MESSAGE)"
clean_volumes:
	make -f scripts/docker_app_makefile clean_volumes

lint:
	./.venv/bin/python -m ruff check .
format:
	./.venv/bin/python -m ruff check --select I --fix . && ./.venv/bin/python -m ruff format .
