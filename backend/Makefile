lint:
	ruff check .

format:
	black .
	ruff check --fix .

test:
	pytest

check: format lint test

install-dev:
	pip install -r requirements.txt

.PHONY: lint format test check install-dev
