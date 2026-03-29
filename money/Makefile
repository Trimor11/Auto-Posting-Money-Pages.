.PHONY: install dev run seed migrate upgrade downgrade lint fmt docker

install:
	python -m venv .venv && .\.venv\Scripts\activate && pip install -r requirements.txt

dev:
	uvicorn app.main:app --reload

seed:
	python -m app.seed_data

migrate:
	alembic revision --autogenerate -m "update"

upgrade:
	alembic upgrade head

downgrade:
	alembic downgrade -1

lint:
	ruff check app

fmt:
	black app

docker:
	docker compose up --build
