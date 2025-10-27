
.PHONY: format lint test all

format:
	black .

lint:
	ruff check .

test:
	pytest -q

all: format lint test
