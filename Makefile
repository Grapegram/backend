ENV_FILE = .env

export ENV_FILE

# Dev
up:
	make -f scripts/docker_app_makefile up
up_bg:
	make -f scripts/docker_app_makefile up_bg
build:
	make -f scripts/docker_app_makefile build
down:
	make -f scripts/docker_app_makefile down

# Prod
prod_up:
	make -f scripts/docker_app_makefile prod_up
prod_up_bg:
	make -f scripts/docker_app_makefile prod_up_bg
prod_build:
	make -f scripts/docker_app_makefile prod_build
prod_down:
	make -f scripts/docker_app_makefile prod_down

# Tools
test:
	make -f scripts/docker_app_makefile test
migrate:
	make -f scripts/docker_app_makefile migrate
migration_create:
	make -f scripts/docker_app_makefile migration_create MESSAGE="$(MESSAGE)"
clean_volumes:
	make -f scripts/docker_app_makefile clean_volumes
