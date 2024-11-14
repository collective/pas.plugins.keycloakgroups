### Defensive settings for make:
#     https://tech.davis-hansson.com/p/make/
SHELL:=bash
.ONESHELL:
.SHELLFLAGS:=-xeu -o pipefail -O inherit_errexit -c
.SILENT:
.DELETE_ON_ERROR:
MAKEFLAGS+=--warn-undefined-variables
MAKEFLAGS+=--no-builtin-rules

# We like colors
# From: https://coderwall.com/p/izxssa/colored-makefile-for-golang-projects
RED=`tput setaf 1`
GREEN=`tput setaf 2`
RESET=`tput sgr0`
YELLOW=`tput setaf 3`

PLONE_VERSION=6.0-latest

# Python checks
PYTHON?=python3

# installed?
ifeq (, $(shell which $(PYTHON) ))
  $(error "PYTHON=$(PYTHON) not found in $(PATH)")
endif

# version ok?
PYTHON_VERSION_MIN=3.8
PYTHON_VERSION_OK=$(shell $(PYTHON) -c "import sys; print((int(sys.version_info[0]), int(sys.version_info[1])) >= tuple(map(int, '$(PYTHON_VERSION_MIN)'.split('.'))))")
ifeq ($(PYTHON_VERSION_OK),0)
  $(error "Need python $(PYTHON_VERSION) >= $(PYTHON_VERSION_MIN)")
endif

REPOSITORY_FOLDER=$(shell dirname $(realpath $(firstword $(MAKEFILE_LIST))))
COMPOSE_FOLDER=${REPOSITORY_FOLDER}/tests
DOCS_DIR=${REPOSITORY_FOLDER}/docs

VENV_FOLDER=$(REPOSITORY_FOLDER)/.venv
BIN_FOLDER=$(VENV_FOLDER)/bin


GIT_FOLDER=$(REPOSITORY_FOLDER)/.git


all: build

# Add the following 'help' target to your Makefile
# And add help text after each target name starting with '\#\#'
.PHONY: help
help: ## This help message
	@grep -E '^[a-zA-Z_-]+:.*?## .*$$' $(MAKEFILE_LIST) | sort | awk 'BEGIN {FS = ":.*?## "}; {printf "\033[36m%-30s\033[0m %s\n", $$1, $$2}'

$(BIN_FOLDER)/uv $(BIN_FOLDER)/uvx $(BIN_FOLDER)/tox:
	@echo "$(GREEN)==> Setup Virtual Env$(RESET)"
	$(PYTHON) -m venv .venv
	$(BIN_FOLDER)/pip install -U "pip" "uv" "tox" "pre-commit"
	if [ -d $(GIT_FOLDER) ]; then $(BIN_FOLDER)/pre-commit install; else echo "$(RED) Not installing pre-commit$(RESET)";fi

instance/etc/zope.ini: $(BIN_FOLDER)/uvx ## Create instance configuration
	@echo "$(GREEN)==> Create instance configuration$(RESET)"
	$(BIN_FOLDER)/uvx cookiecutter -f --no-input --config-file instance.yaml gh:plone/cookiecutter-zope-instance

.PHONY: config
config: instance/etc/zope.ini

requirements-mxdev.txt constraints-mxdev.txt: $(BIN_FOLDER)/uvx ## Generate constraints file
	@echo "$(GREEN)==> Generate constraints file$(RESET)"
	@echo '-c https://dist.plone.org/release/$(PLONE_VERSION)/constraints.txt' > requirements.txt
	$(BIN_FOLDER)/uvx mxdev -c mx.ini

$(BIN_FOLDER)/runwsgi: $(BIN_FOLDER)/uvx ## Install Plone
	@echo "$(GREEN)==> Install Plone Build$(RESET)"
	$(BIN_FOLDER)/uv pip install -r requirements-mxdev.txt

.PHONY: build-dev
build-dev: constraints-mxdev.txt config $(BIN_FOLDER)/runwsgi ## install Plone packages

.PHONY: install
install: build-dev ## Install Plone 6.0

.PHONY: build
build: build-dev ## Install Plone 6.0

.PHONY: clean
clean: ## Remove old virtualenv and creates a new one
	@echo "$(RED)==> Cleaning environment and build$(RESET)"
	rm -rf bin lib lib64 include share etc var inituser pyvenv.cfg .installed.cfg .tox $(VENV_FOLDER) .pytest_cache *-mxdev.txt

.PHONY: clean-data
clean-data: ## Remove instance data
	@echo "$(RED)==> Cleaning instance and build$(RESET)"
	rm -rf instance

.PHONY: start
start: $(BIN_FOLDER)/runwsgi ## Start a Plone instance on localhost:8080
	PYTHONWARNINGS=ignore $(BIN_FOLDER)/runwsgi instance/etc/zope.ini

.PHONY: console
console: ## Start a zope console
	PYTHONWARNINGS=ignore $(BIN_FOLDER)/zconsole debug instance/etc/zope.conf

.PHONY: format
format: $(BIN_FOLDER)/tox ## Format the codebase according to our standards
	@echo "$(GREEN)==> Format codebase$(RESET)"
	$(BIN_FOLDER)/tox -e format

.PHONY: lint
lint: ## check code style
	$(BIN_FOLDER)/tox -e lint

# i18n
$(BIN_FOLDER)/i18ndude: $(BIN_FOLDER)/pipx
	@echo "$(GREEN)==> Install translation tools$(RESET)"
	$(BIN_FOLDER)/pip install i18ndude

.PHONY: i18n
i18n: $(BIN_FOLDER)/i18ndude ## Update locales
	@echo "$(GREEN)==> Updating locales$(RESET)"
	$(BIN_FOLDER)/update_dist_locale

# Tests
.PHONY: test
test: $(BIN_FOLDER)/tox ## run tests
	$(BIN_FOLDER)/tox -e test

.PHONY: test-coverage
test-coverage: $(BIN_FOLDER)/tox ## run tests with coverage
	$(BIN_FOLDER)/tox -e coverage

# Keycloak
.PHONY: keycloak-start
keycloak-start: ## Start Keycloak stack
	@echo "$(GREEN)==> Start keycloak stack$(RESET)"
	@docker compose -f $(COMPOSE_FOLDER)/docker-compose.yml up -d

.PHONY: keycloak-status
keycloak-status: ## Check Keycloak stack status
	@echo "$(GREEN)==> Check Keycloak stack status$(RESET)"
	@docker compose -f $(COMPOSE_FOLDER)/docker-compose.yml ps

.PHONY: keycloak-stop
keycloak-stop: ## Stop Keycloak stack
	@echo "$(GREEN)==> Stop Keycloak stack$(RESET)"
	@docker compose -f $(COMPOSE_FOLDER)/docker-compose.yml down

# Docs
$(BIN_FOLDER)/sphinx-build: $(BIN_FOLDER)/pipx
	$(BIN_FOLDER)/pip install -r requirements-docs.txt

.PHONY: docs-build
docs-build: $(BIN_FOLDER)/sphinx-build  ## Build the documentation
	$(BIN_FOLDER)/sphinx-build \
		-b html $(DOCS_DIR) "$(DOCS_DIR)/_build/html"

.PHONY: docs-live
docs-live: $(BIN_FOLDER)/sphinx-build  ## Rebuild Sphinx documentation on changes, with live-reload in the browser
	$(BIN_FOLDER)/sphinx-autobuild \
		--ignore "*.swp" \
		-b html $(DOCS_DIR) "$(DOCS_DIR)/_build/html"

# Release Tasks
.PHONY: release
release: $(BIN_FOLDER)/uvx  ## Release package to pypi.org
	$(BIN_FOLDER)/fullrelease
