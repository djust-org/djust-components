# djust-components - Makefile

# Colors for output
BLUE := \033[0;34m
GREEN := \033[0;32m
YELLOW := \033[0;33m
RED := \033[0;31m
NC := \033[0m # No Color

.DEFAULT_GOAL := help

##@ Help

.PHONY: help
help: ## Display this help message
	@echo "$(BLUE)djust-components - Development Commands$(NC)"
	@echo ""
	@awk 'BEGIN {FS = ":.*##"; printf "Usage:\n  make $(YELLOW)<target>$(NC)\n"} /^[a-zA-Z_0-9-]+:.*?##/ { printf "  $(GREEN)%-20s$(NC) %s\n", $$1, $$2 } /^##@/ { printf "\n$(BLUE)%s$(NC)\n", substr($$0, 5) } ' $(MAKEFILE_LIST)

##@ Development

.PHONY: install
install: ## Install package in editable mode with dev dependencies
	@echo "$(GREEN)Installing djust-components...$(NC)"
	@uv pip install -e ".[dev]"

.PHONY: test
test: ## Run all tests
	@echo "$(GREEN)Running tests...$(NC)"
	@.venv/bin/python -m pytest tests/ -v

.PHONY: lint
lint: ## Run linters
	@echo "$(GREEN)Running linters...$(NC)"
	@ruff check src/ tests/
	@ruff format --check src/ tests/

.PHONY: format
format: ## Format all code
	@echo "$(GREEN)Formatting code...$(NC)"
	@ruff format src/ tests/

##@ Release

.PHONY: version
version: ## Bump version (usage: make version VERSION=0.4.0rc1)
ifndef VERSION
	@echo "$(RED)ERROR: VERSION not specified$(NC)"
	@echo "Usage: make version VERSION=0.4.0rc1"
	@exit 1
endif
	@echo "$(GREEN)Bumping version to $(VERSION)...$(NC)"
	@# Update pyproject.toml
	@sed 's/^version = ".*"/version = "$(VERSION)"/' pyproject.toml > pyproject.toml.tmp && mv pyproject.toml.tmp pyproject.toml
	@# Update __version__ in __init__.py
	@sed 's/^__version__ = ".*"/__version__ = "$(VERSION)"/' src/djust_components/__init__.py > src/djust_components/__init__.py.tmp && mv src/djust_components/__init__.py.tmp src/djust_components/__init__.py
	@echo "$(GREEN)Updated versions:$(NC)"
	@echo "  pyproject.toml: $(VERSION)"
	@echo "  __init__.py:    $(VERSION)"
	@echo "$(YELLOW)Don't forget to update CHANGELOG.md!$(NC)"

.PHONY: version-check
version-check: ## Check current version in all files
	@echo "$(BLUE)Current versions:$(NC)"
	@echo "  pyproject.toml: $$(grep '^version = ' pyproject.toml | head -1)"
	@echo "  __init__.py:    $$(grep '^__version__' src/djust_components/__init__.py | head -1)"

.PHONY: release
release: ## Create and push a release tag (usage: make release VERSION=0.4.0rc1)
ifndef VERSION
	@echo "$(RED)ERROR: VERSION not specified$(NC)"
	@echo "Usage: make release VERSION=0.4.0rc1"
	@exit 1
endif
	@echo "$(YELLOW)Creating release v$(VERSION)...$(NC)"
	@# Verify we're on main or release branch
	@BRANCH=$$(git branch --show-current); \
	if [ "$$BRANCH" != "main" ] && ! echo "$$BRANCH" | grep -q "^release/"; then \
		echo "$(RED)ERROR: Must be on main or release/* branch$(NC)"; \
		exit 1; \
	fi
	@# Verify working directory is clean
	@if [ -n "$$(git status --porcelain)" ]; then \
		echo "$(RED)ERROR: Working directory not clean$(NC)"; \
		git status --short; \
		exit 1; \
	fi
	@# Verify versions match
	@PY_VERSION=$$(grep '^version = ' pyproject.toml | head -1 | sed 's/version = "//; s/"//'); \
	if [ "$$PY_VERSION" != "$(VERSION)" ]; then \
		echo "$(RED)ERROR: Version mismatch - pyproject.toml has $$PY_VERSION$(NC)"; \
		echo "Run: make version VERSION=$(VERSION)"; \
		exit 1; \
	fi
	@# Create and push tag
	@git tag -a v$(VERSION) -m "Release v$(VERSION)"
	@git push origin v$(VERSION)
	@echo "$(GREEN)Release v$(VERSION) created and pushed!$(NC)"
	@echo "$(YELLOW)GitHub Actions will build and publish to PyPI$(NC)"

.PHONY: release-dry-run
release-dry-run: ## Show what would be released (dry run)
ifndef VERSION
	@echo "$(RED)ERROR: VERSION not specified$(NC)"
	@echo "Usage: make release-dry-run VERSION=0.4.0rc1"
	@exit 1
endif
	@echo "$(BLUE)Release dry run for v$(VERSION)$(NC)"
	@echo ""
	@echo "$(YELLOW)Current branch:$(NC) $$(git branch --show-current)"
	@echo "$(YELLOW)Working directory:$(NC) $$(if [ -n "$$(git status --porcelain)" ]; then echo 'dirty'; else echo 'clean'; fi)"
	@echo ""
	@echo "$(YELLOW)Version files:$(NC)"
	@echo "  pyproject.toml: $$(grep '^version = ' pyproject.toml | head -1)"
	@echo "  __init__.py:    $$(grep '^__version__' src/djust_components/__init__.py | head -1)"
	@echo ""
	@echo "$(YELLOW)Changes since last tag:$(NC)"
	@git log --oneline $$(git describe --tags --abbrev=0 2>/dev/null || echo HEAD~10)..HEAD | head -20
	@echo ""
	@echo "$(YELLOW)Would create tag:$(NC) v$(VERSION)"
	@if echo "$(VERSION)" | grep -qE '[ab]|rc'; then \
		echo "$(YELLOW)Pre-release:$(NC) yes"; \
	else \
		echo "$(YELLOW)Pre-release:$(NC) no (stable)"; \
	fi
