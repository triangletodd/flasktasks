# FlaskTasks Makefile
# Provides convenient targets for testing, development, and project management

.PHONY: help test test-all test-unittest test-pytest test-simple test-app test-templates test-coverage clean install run dev lint format check setup

# Default target
help:
	@echo "FlaskTasks - Available Make Targets:"
	@echo ""
	@echo "Testing:"
	@echo "  make test          - Run all test suites (default)"
	@echo "  make test-all      - Run all test suites with detailed output"
	@echo "  make test-unittest - Run all unittest test suites"
	@echo "  make test-pytest   - Run pytest test suite"
	@echo "  make test-simple   - Run simple core functionality tests"
	@echo "  make test-app      - Run extended application tests"
	@echo "  make test-templates - Run HTML template and UI tests"
	@echo "  make test-coverage - Run tests with coverage reporting"
	@echo ""
	@echo "Development:"
	@echo "  make install       - Install dependencies"
	@echo "  make run           - Run the Flask application"
	@echo "  make dev           - Run in development mode with debug"
	@echo "  make clean         - Clean up temporary files"
	@echo ""
	@echo "Code Quality:"
	@echo "  make lint          - Run linting (if flake8 available)"
	@echo "  make format        - Format code (if black available)"
	@echo "  make check         - Run all quality checks"
	@echo ""
	@echo "Setup:"
	@echo "  make setup         - Initial project setup"

# Testing Targets
test: test-all
	@echo "✅ All tests completed successfully!"

test-all:
	@echo "🧪 Running all test suites..."
	@python run_tests.py all

test-unittest:
	@echo "🧪 Running unittest test suites..."
	@python run_tests.py unittest

test-pytest:
	@echo "🧪 Running pytest test suite..."
	@python run_tests.py pytest

test-simple:
	@echo "🧪 Running simple core functionality tests..."
	@python -m unittest test_simple.py -v

test-app:
	@echo "🧪 Running extended application tests..."
	@python -m unittest test_app.py -v

test-templates:
	@echo "🧪 Running HTML template and UI tests..."
	@python -m unittest test_templates.py -v

test-coverage:
	@echo "📊 Running tests with coverage reporting..."
	@python run_tests.py coverage
	@echo "📊 Coverage report generated in htmlcov/index.html"

# Development Targets
install:
	@echo "📦 Installing dependencies..."
	@pip install -r requirements.txt

run:
	@echo "🚀 Starting FlaskTasks application..."
	@python app.py

dev:
	@echo "🔧 Starting FlaskTasks in development mode..."
	@export FLASK_ENV=development && python app.py

# Code Quality Targets
lint:
	@echo "🔍 Running linting..."
	@if command -v flake8 >/dev/null 2>&1; then \
		flake8 app.py test_*.py --max-line-length=100; \
	else \
		echo "⚠️  flake8 not installed. Run: pip install flake8"; \
	fi

format:
	@echo "✨ Formatting code..."
	@if command -v black >/dev/null 2>&1; then \
		black app.py test_*.py --line-length=100; \
	else \
		echo "⚠️  black not installed. Run: pip install black"; \
	fi

check: lint test
	@echo "✅ All quality checks passed!"

# Cleanup Targets
clean:
	@echo "🧹 Cleaning up temporary files..."
	@find . -type f -name "*.pyc" -delete
	@find . -type d -name "__pycache__" -exec rm -rf {} + 2>/dev/null || true
	@find . -type f -name "*.db" -path "./test_*" -delete 2>/dev/null || true
	@rm -rf .pytest_cache
	@rm -rf htmlcov
	@rm -rf .coverage
	@rm -rf *.egg-info
	@echo "✅ Cleanup completed!"

# Setup Targets
setup: install
	@echo "🏗️  Setting up FlaskTasks development environment..."
	@python -c "from app import init_db; init_db()"
	@echo "✅ Setup completed! You can now run 'make test' or 'make run'"

# Quick Development Workflow Targets
quick-test: test-simple
	@echo "⚡ Quick test completed!"

full-check: clean install test-coverage lint
	@echo "🎯 Full project check completed!"

# Database Management
init-db:
	@echo "🗃️  Initializing database..."
	@python -c "from app import init_db; init_db(); print('Database initialized successfully!')"

reset-db:
	@echo "🔄 Resetting database..."
	@rm -f todos.db
	@python -c "from app import init_db; init_db(); print('Database reset successfully!')"

# Documentation
docs:
	@echo "📚 Generating documentation..."
	@echo "Available documentation files:"
	@echo "  - README.md (Main documentation)"
	@echo "  - TESTING.md (Testing documentation)" 
	@echo "  - run_tests.py --help (Test runner help)"

# Project Information
info:
	@echo "📋 FlaskTasks Project Information:"
	@echo "  Name: FlaskTasks"
	@echo "  Description: A task management application built with Flask"
	@echo "  Python Files: $(shell find . -name '*.py' | wc -l)"
	@echo "  Test Files: $(shell find . -name 'test_*.py' | wc -l)"
	@echo "  Total Tests: 65 (across all test suites)"
	@echo "  Database: SQLite (todos.db)"
	@echo "  Framework: Flask + Bootstrap"