.PHONY: help lint type smoke check clean run install

help:  ## Show this help message
	@echo "Available targets:"
	@grep -E '^[a-zA-Z_-]+:.*?## .*$$' $(MAKEFILE_LIST) | sort | awk 'BEGIN {FS = ":.*?## "}; {printf "  \033[36m%-15s\033[0m %s\n", $$1, $$2}'

install:  ## Install dependencies
	pip install -r requirements.txt

lint:  ## Run ruff linting
	@echo "=== Running Ruff linter ==="
	@python -m ruff check . --fix || (echo "❌ Linting failed" && exit 1)
	@echo "✓ Linting passed"

type:  ## Run mypy type checking
	@echo "=== Running Mypy type checker ==="
	@python -m mypy products core || (echo "❌ Type checking failed" && exit 1)
	@echo "✓ Type checking passed"

smoke:  ## Run smoke import tests
	@echo "=== Running Smoke Tests ==="
	@python tests/smoke_imports.py || (echo "❌ Smoke tests failed" && exit 1)

check: lint type smoke validate-faq-recs  ## Run all checks (lint + type + smoke + faq validation)
	@echo ""
	@echo "✅ All checks passed!"

format:  ## Format code with ruff
	@echo "=== Formatting code with Ruff ==="
	@python -m ruff format .
	@echo "✓ Code formatted"

clean:  ## Remove cache and temporary files
	@echo "=== Cleaning cache files ==="
	@find . -type d -name "__pycache__" -exec rm -rf {} + 2>/dev/null || true
	@find . -name "*.pyc" -delete 2>/dev/null || true
	@find . -name "*.pyo" -delete 2>/dev/null || true
	@find . -name ".DS_Store" -delete 2>/dev/null || true
	@rm -rf .ruff_cache .mypy_cache .pytest_cache 2>/dev/null || true
	@echo "✓ Cache cleaned"

run:  ## Run the Streamlit app
	@echo "=== Starting Streamlit app ==="
	@streamlit run app.py

test:  ## Run pytest tests
	@echo "=== Running pytest ==="
	@pytest tests/ -v

watch:  ## Run app with auto-reload (development mode)
	@echo "=== Starting Streamlit in watch mode ==="
	@streamlit run app.py --server.runOnSave true

stats:  ## Show repository statistics
	@echo "=== Repository Statistics ==="
	@echo "Python files:    $$(find . -name '*.py' -type f ! -path './venv/*' ! -path './archive/*' | wc -l | tr -d ' ')"
	@echo "Products:        $$(find products -maxdepth 1 -type d ! -name products ! -name __pycache__ | wc -l | tr -d ' ')"
	@echo "Hubs:            $$(ls -1 hubs/*.py 2>/dev/null | wc -l | tr -d ' ')"
	@echo "Pages:           $$(ls -1 pages/*.py 2>/dev/null | wc -l | tr -d ' ')"
	@echo "Core modules:    $$(ls -1 core/*.py 2>/dev/null | wc -l | tr -d ' ')"
	@echo "Static images:   $$(find static/images -type f | wc -l | tr -d ' ')"
	@echo "Lines of code:   $$(find . -name '*.py' -type f ! -path './venv/*' ! -path './archive/*' -exec wc -l {} + | tail -1 | awk '{print $$1}')"

sync-site:  ## Crawl CCA website and update corp knowledge base
	@echo "=== Syncing Corporate Knowledge Base ==="
	@python tools/sync_site.py || (echo "❌ Site sync failed" && exit 1)
	@echo "✓ Knowledge base updated"

validate-faq-recs:  ## Validate recommended FAQ chips have valid answers
	@echo "=== Validating FAQ Recommended Questions ==="
	@python tools/validate_faq_recs.py || (echo "❌ FAQ validation failed" && exit 1)
