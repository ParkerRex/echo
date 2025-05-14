lint:
	ruff check .

format:
	black .
	ruff check --fix .

test:
	pytest

check: format lint test

install-dev:
	pip install -e ".[dev]"

run-local:
	uvicorn video_processor.infrastructure.api.server:app --reload --port 8080

.PHONY: lint format test check install-dev run-local
