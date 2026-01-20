# Khareetaty AI - Kuwait National Intelligence Platform
# Makefile for local development

.PHONY: run lint test clean help

help:
	@echo "Khareetaty AI - Kuwait National Intelligence Platform"
	@echo ""
	@echo "Available commands:"
	@echo "  make run    - Run Streamlit app locally"
	@echo "  make lint   - Run code linting with ruff"
	@echo "  make test   - Run tests (if available)"
	@echo "  make clean  - Clean cache and temporary files"

run:
	@echo "Starting Khareetaty AI..."
	streamlit run app.py

lint:
	@echo "Running linter..."
	@command -v ruff >/dev/null 2>&1 || { echo "ruff not installed. Install with: pip install ruff"; exit 1; }
	ruff check .

test:
	@echo "Running tests..."
	@command -v pytest >/dev/null 2>&1 || { echo "pytest not installed. Install with: pip install pytest"; exit 1; }
	pytest tests/ -v

clean:
	@echo "Cleaning cache and temporary files..."
	find . -type d -name "__pycache__" -exec rm -rf {} + 2>/dev/null || true
	find . -type d -name ".pytest_cache" -exec rm -rf {} + 2>/dev/null || true
	find . -type f -name "*.pyc" -delete 2>/dev/null || true
	rm -rf .streamlit/cache 2>/dev/null || true
	@echo "Clean complete!"
