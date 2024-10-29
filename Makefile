# Makefile

up-dev: # поднять контейнеры
	docker compose -f docker/local-docker-compose.yaml -p optisense up -d --force-recreate --remove-orphans || true

restart-dev: # перезапустить контейнеры
	docker compose -f docker/local-docker-compose.yaml -p optisense restart

down-dev: # остановить и удалить контейнеры
	docker compose -f docker/local-docker-compose.yaml -p optisense down

inspectdb: # создает модели на основе структуры таблиц в базе данных
	docker exec -it optisense-app python src/optisense/manage.py inspectdb

migrations: # создает миграции на основе Django моделей
	docker exec -it optisense-app python src/optisense/manage.py makemigrations

migrate: # применяет миграции
	docker exec -it optisense-app python src/optisense/manage.py migrate
