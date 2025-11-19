# Echo Nexus Makefile

.PHONY: all build test lint clean docs install check-env

all: build test

# Installation
install:
	pip install -e sdk/python[dev]
	cd sdk/typescript && npm install

# Build
build:
	cd sdk/python && python -m build
	cd sdk/typescript && npm run build
	cd sdk/rust && cargo build --release

# Testing
test: test-python test-typescript test-rust

test-python:
	pytest sdk/python/tests -v --cov=echo_nexus

test-typescript:
	cd sdk/typescript && npm test

test-rust:
	cd sdk/rust && cargo test

test-engine:
	pytest engines/$(ENGINE)/tests -v

# Linting
lint: lint-python lint-typescript lint-rust

lint-python:
	black --check sdk/python
	mypy sdk/python/src

lint-typescript:
	cd sdk/typescript && npm run lint

lint-rust:
	cd sdk/rust && cargo clippy

# Format
format:
	black sdk/python
	cd sdk/typescript && npm run format
	cd sdk/rust && cargo fmt

# Documentation
docs:
	mkdocs build

docs-serve:
	mkdocs serve

# Clean
clean:
	rm -rf sdk/python/dist sdk/python/*.egg-info
	rm -rf sdk/typescript/dist
	rm -rf sdk/rust/target
	find . -type d -name __pycache__ -exec rm -rf {} +
	find . -type f -name "*.pyc" -delete

# Environment check
check-env:
	@echo "Checking environment..."
	@python --version
	@node --version
	@cargo --version || echo "Rust not installed"
	@echo "Environment OK"

# Help
help:
	@echo "Echo Nexus Build Commands:"
	@echo "  make install    - Install dependencies"
	@echo "  make build      - Build all SDKs"
	@echo "  make test       - Run all tests"
	@echo "  make lint       - Run linters"
	@echo "  make docs       - Build documentation"
	@echo "  make clean      - Clean build artifacts"
