.PHONY: help install install-dev test lint format clean build

help: ## Show this help message
	@echo "Available targets:"
	@grep -E '^[a-zA-Z_-]+:.*?## .*$$' $(MAKEFILE_LIST) | awk 'BEGIN {FS = ":.*?## "}; {printf "  %-15s %s\n", $$1, $$2}'

install: ## Install package in production mode
	uv pip install -e .

install-dev: ## Install package with dev dependencies
	uv pip install -e ".[dev]"

test: ## Run tests with pytest
	pytest

test-cov: ## Run tests with coverage report
	pytest --cov=reportit --cov-report=term-missing --cov-report=html

lint: ## Run ruff linter
	ruff check reportit tests

format: ## Format code with black
	black reportit tests

format-check: ## Check code formatting without making changes
	black --check reportit tests

lint-fix: ## Run ruff with auto-fix
	ruff check --fix reportit tests

check: lint format-check ## Run all checks (lint and format)

clean: ## Clean build artifacts and cache
	rm -rf build/
	rm -rf dist/
	rm -rf *.egg-info
	rm -rf .pytest_cache
	rm -rf .ruff_cache
	rm -rf htmlcov/
	rm -rf .coverage
	find . -type d -name __pycache__ -exec rm -r {} +
	find . -type f -name "*.pyc" -delete

build: clean ## Build distribution packages
	uv build

all: clean install-dev lint format-check test ## Run all checks and tests
