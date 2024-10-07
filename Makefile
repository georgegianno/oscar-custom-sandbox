VENV = venv
PYTEST = $(PWD)/$(VENV)/bin/py.test

# These targets are not files
.PHONY: build_sandbox clean compile_translations coverage css docs extract_translations help install install-python \
 install-test install-js lint release retest sandbox_clean sandbox_image sandbox test todo venv package

help: ## Display this help message
	@echo "Please use \`make <target>\` where <target> is one of"
	@grep -E '^[a-zA-Z_-]+:.*?## .*$$' $(MAKEFILE_LIST) | sort | awk 'BEGIN {FS = ":.*?## "}; \
	{printf "\033[36m%-40s\033[0m %s\n", $$1, $$2}'

##################
# Install commands
##################
install: install-python install-test assets ## Install requirements for local development and production

install-python: ## Install python requirements
	pip install -r requirements.txt --upgrade --upgrade-strategy=eager

install-test: ## Install test requirements
	pip install -e .[test] --upgrade --upgrade-strategy=eager

install-migrations-testing-requirements: ## Install migrations testing requirements
	pip install -r requirements_migrations.txt

assets: ## Install static assets
	npm install
	npm run build

venv: ## Create a virtual env and install test and production requirements
	$(shell which python3) -m venv $(VENV) --upgrade-deps
	$(VENV)/bin/pip install -e .[test]
	$(VENV)/bin/pip install -r docs/requirements.txt

sandbox: 
	pip install --upgrade pip 
	pip install -r requirements.txt
	@echo "Running sandbox setup..."
	@echo "export PYTHONPATH=$(PWD)/src:\$$PYTHONPATH"
