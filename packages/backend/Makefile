# Force Git Bash on Windows 
SHELL := C:/Program Files/Git/bin/bash.exe

# Testing
test:
	uv run pytest

test-unit:
	uv run pytest -m unit

test-integration:
	uv run pytest -m integration

test-cov:
	uv run pytest --cov=app --cov-report=term-missing

# Validation (combines all quality checks)
validate:
	@echo "Running all validation checks..."
	uv run mypy app/
	uv run ruff check app/
	uv run ruff format --check app/
	uv run pytest

# Linting
lint:
	bash scripts/lint.sh

# Cleaning
clean:
	find . -type d -name "__pycache__" -exec rm -rf {} +
	find . -type d -name ".mypy_cache" -exec rm -rf {} +
	find . -type d -name ".ruff_cache" -exec rm -rf {} +
	find . -type d -name ".pytest_cache" -exec rm -rf {} +
	find . -type f -name "*.pyc" -delete
	find . -type f -name "*.pyo" -delete
	find . -type f -name ".coverage" -delete


# Help command
help:
	@echo "Available commands:"
	@echo "  test         : Run all tests"
	@echo "  test-unit    : Run only unit tests"
	@echo "  test-integration : Run only integration tests"
	@echo "  test-cov     : Run tests with coverage report"
	@echo "  validate     : Run all validation checks (mypy, ruff, pytest)"
	@echo "  lint         : Run code formatters and linters"
	@echo "  clean        : Remove Python cache files and build artifacts"
