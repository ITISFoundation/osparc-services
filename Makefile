# author: Sylvain Anderegg

VERSION := $(shell uname -a)

export VCS_URL:=$(shell git config --get remote.origin.url)
export VCS_REF:=$(shell git rev-parse --short HEAD)
export VCS_STATUS_CLIENT:=$(if $(shell git status -s),'modified/untracked','clean')
export BUILD_DATE:=$(shell date -u +"%Y-%m-%dT%H:%M:%SZ")


.PHONY: help
help: ## help on rule's targets
	@awk --posix 'BEGIN {FS = ":.*?## "} /^[[:alpha:][:space:]_-]+:.*?## / {printf "\033[36m%-20s\033[0m %s\n", $$1, $$2}' $(MAKEFILE_LIST)

.DEFAULT_GOAL := help


.PHONY: new-service
new-service: ## Bakes a new project from cookiecutter-simcore-pyservice and drops it under services/
	.venv/bin/cookiecutter gh:ITISFoundation/cookiecutter-osparc-service --output-dir $(CURDIR)/services


.PHONY: info
info: ## Displays some parameters of makefile environments
	@echo '+ VCS_* '
	@echo '  - ULR                : ${VCS_URL}'
	@echo '  - REF                : ${VCS_REF}'
	@echo '  - (STATUS)REF_CLIENT : (${VCS_STATUS_CLIENT})'
	@echo '+ BUILD_DATE           : ${BUILD_DATE}'
	@echo '+ VERSION              : ${VERSION}'
	@echo '+ DOCKER_REGISTRY      : ${DOCKER_REGISTRY}'


.PHONY: devenv
devenv: .venv
.venv: ## Creates a python virtual environment with dev tools (pip, pylint, ...)
	python3 -m venv .venv
	.venv/bin/pip3 install --upgrade pip wheel setuptools
	.venv/bin/pip3 install pylint black cookiecutter semver
	.venv/bin/pip3 install -r scripts/auto-doc/requirements.txt
	@echo "To activate the venv, execute 'source .venv/bin/activate'"


.PHONY: toc
toc: .venv ## Updates README.txt with a ToC of all services
	@.venv/bin/python ${CURDIR}/scripts/auto-doc/create-toc.py 

.PHONY: resource-upgrade-stubs
resource-upgrade-stubs: toc ## retag images
	@.venv/bin/python ${CURDIR}/scripts/resources/create_update_stubs.py --toc=${CURDIR}/toc.json


.PHONY: clean
clean:  ## Cleans all unversioned files in project
	@git clean -dxf -e .vscode/
