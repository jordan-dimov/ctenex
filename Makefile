DIRS = ctenex/ tests/

.PHONY: lint format type-check test coverage

# Default to --fix, can be overridden with make lint DIFF=1
DIFF_LINT_FLAG = $(if $(DIFF),--diff,--fix)
# Default to empty, can be overridden with make format DIFF=1
DIFF_FORMAT_FLAG = $(if $(DIFF),--diff,)

lint:
	poetry run ruff check $(DIFF_LINT_FLAG) $(DIRS) && poetry run ruff check --select I $(DIFF_LINT_FLAG) $(DIRS)

format:
	poetry run ruff format $(DIFF_FORMAT_FLAG) $(DIRS)

type-check:
	poetry run pyright $(DIRS)

test:
	poetry run coverage run -m pytest tests --full-trace

coverage:
	poetry run coverage report -m

coverage-html:
	poetry run coverage html

# Convenience target to run all checks
check: lint format type-check test coverage coverage-html
