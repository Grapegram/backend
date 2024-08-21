export DOCKER_DEFAULT_PLATFORM=linux/amd64


postgres_up:
	docker compose -f docker-compose-postgres.yaml up -d

postgres_down:
	docker compose -f docker-compose-postgres.yaml down --remove-orphans
