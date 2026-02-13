.PHONY: up down reset migrate test

up:
	docker compose up --build

down:
	docker compose down

reset:
	docker compose down -v && rm -f storage/app.db

migrate:
	docker compose run --rm migrate

test:
	docker compose --profile test run --rm test
