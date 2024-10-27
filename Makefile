# Makefile

up-dev: # поднять контейнеры
	docker compose -f docker/local-docker-compose.yaml -p optisense up -d --force-recreate --remove-orphans || true

restart-dev: # перезапустить контейнеры
	docker compose -f docker/local-docker-compose.yaml -p optisense restart

down-dev: # остановить и удалить контейнеры
	docker compose -f docker/local-docker-compose.yaml -p optisense down

