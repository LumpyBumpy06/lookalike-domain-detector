PYTHON ?= python3

.PHONY: install fmt lint typecheck test check

install:
	$(PYTHON) -m pip install -e ".[dev]"

fmt:
	ruff format .
	ruff check --fix .

lint:
	ruff format --check .
	ruff check .

typecheck:
	mypy --strict src

test:
	pytest --cov=lookalike --cov-branch --cov-fail-under=90

check: lint typecheck test
