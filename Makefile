# Makefile

up: # поднять контейнеры
	docker compose -f docker/docker-compose.yaml -p optisense up -d --force-recreate --remove-orphans || true

restart: # перезапустить контейнеры в режиме разработки
	docker compose -f docker/docker-compose.yaml -p optisense restart

down: # остановить и удалить контейнеры
	docker compose -f docker/docker-compose.yaml -p optisense down

up-dev: # поднять контейнеры в режиме разработки
	docker compose -f docker/dev-docker-compose.yaml -p optisense up -d --force-recreate --remove-orphans || true

restart-dev: # перезапустить контейнеры в режиме разработки
	docker compose -f docker/dev-docker-compose.yaml -p optisense restart

down-dev: # остановить и удалить контейнеры в режиме разработки
	docker compose -f docker/dev-docker-compose.yaml -p optisense down

inspectdb: # создает модели на основе структуры таблиц в базе данных
	docker exec -it optisense-app python src/optisense/manage.py inspectdb

migrations: # создает миграции на основе Django моделей
	docker exec -it optisense-app python src/optisense/manage.py makemigrations

migrate: # применяет миграции
	docker exec -it optisense-app python src/optisense/manage.py migrate

generate-test-data: # генерация тестовых данных
	docker exec -it optisense-app python src/optisense/manage.py generate_test_data