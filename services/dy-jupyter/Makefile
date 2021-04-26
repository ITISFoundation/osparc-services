VERSION := $(shell cat /proc/version)


# using ?= will only set if absent
export DOCKER_IMAGE_TAG ?= $(shell cat VERSION)
$(info DOCKER_IMAGE_TAG set to ${DOCKER_IMAGE_TAG})

# default to local (no registry)
export DOCKER_REGISTRY ?= itisfoundation
$(info DOCKER_REGISTRY set to ${DOCKER_REGISTRY})

export VCS_URL:=$(shell git config --get remote.origin.url)
export VCS_REF=$(shell git rev-parse --short HEAD)
export BUILD_DATE=$(shell date -u +"%Y-%m-%dT%H:%M:%SZ")

## Tools ------------------------------------------------------------------------------------------------------
#
tools =

ifeq ($(shell uname -s),Darwin)
	SED = gsed
else
	SED = sed
endif

ifeq ($(shell which ${SED}),)
	tools += $(SED)
endif

.PHONY: all
all: help info
ifdef tools
	$(error "Can't find tools:${tools}")
endif

.PHONY: build rebuild
# target: build, rebuild: – Builds all service images. Use `rebuild` to build w/o cache.
build:
	docker buildx > /dev/null; export DOCKER_CLI_EXPERIMENTAL=enabled; docker buildx bake --file docker-compose.yml

rebuild:
	docker buildx > /dev/null; export DOCKER_CLI_EXPERIMENTAL=enabled; docker buildx bake --file docker-compose.yml --no-cache

.PHONY: build-devel
# target: build-devel: – Builds images of core services for development.
build-devel:
	docker buildx > /dev/null; export DOCKER_CLI_EXPERIMENTAL=enabled; docker buildx bake --file docker-compose.yml --file docker-compose.devel.yml

.PHONY: up up-devel down
# target: up, down: – starts/stops service
# target: up-devel: – deploys service in devel mode together with minimal swarm-like environment
up: .env
	docker-compose --file docker-compose.yml up

up-devel: .env
	@mkdir -p notebook-inputs
	@mkdir -p notebook-outputs
	@mkdir -p retrieval-data
	docker-compose --file docker-compose.yml --file docker-compose.devel.yml up

down: .env
	docker-compose --file docker-compose.yml --file docker-compose.devel.yml down
	docker-compose --file docker-compose.yml down


.PHONY: push pull
# target: push – Pushes the service images to ${DOCKER_REGISTRY}
# target: pull - Pulls the service images from ${DOCKER_REGISTRY}
push:
	docker-compose --file docker-compose.yml push

pull:
	docker-compose --file docker-compose.yml pull

test:
	# tests https://github.com/ITISFoundation/osparc-services/issues/15
	docker run --entrypoint python3 ${DOCKER_REGISTRY}/jupyter-base-notebook:${DOCKER_IMAGE_TAG} -c "import psycopg2"
	docker run --entrypoint python3 ${DOCKER_REGISTRY}/jupyter-scipy-notebook:${DOCKER_IMAGE_TAG} -c "import psycopg2"
	docker run --entrypoint python3 ${DOCKER_REGISTRY}/jupyter-r-notebook:${DOCKER_IMAGE_TAG} -c "import psycopg2"
	@echo 'test passed'

## -------------------------------
# Tools

.PHONY: info
# target: info – Displays some parameters of makefile environments
info: .env
	@echo '+ VCS_* '
	@echo '  - URL                : ${VCS_URL}'
	@echo '  - REF                : ${VCS_REF}'
	@echo '+ BUILD_DATE           : ${BUILD_DATE}'
	@echo '+ VERSION              : ${VERSION}'
	@echo '+ DOCKER_REGISTRY      : ${DOCKER_REGISTRY}'
	@echo '+ DOCKER_IMAGE_TAG     : ${DOCKER_IMAGE_TAG}'

PHONY: .env
.env: .env-devel
	# first check if file exists, copies it
	@if [ ! -f $@ ]	; then \
		echo "##### $@ does not exist, copying $< ############"; \
		cp $< $@; \
	else \
		echo "#####  $< is newer than $@ ####"; \
		diff -uN $@ $<; \
		false; \
	fi

.vscode/settings.json: .vscode-template/settings.json
	$(info #####  $< is newer than $@ ####)
	@diff -uN $@ $<
	@false

PHONY: setup-check
# target: setup-check – Checks whether setup is in sync with templates (e.g. vscode settings or .env file)
setup-check: .env .vscode/settings.json


## -------------------------------
# Virtual Environments
PHONY: .venv
.venv:
# target: .venv – Creates a python virtual environment with dev tools (pip, pylint, ...)
	python3 -m venv .venv
	.venv/bin/pip3 install --upgrade pip wheel setuptools
	.venv/bin/pip3 install pylint autopep8 virtualenv
	@echo "To activate the venv, execute 'source .venv/bin/activate' or '.venv/bin/activate.bat' (WIN)"

## -------------------------------
# Auxiliary targets.

.PHONY: clean
# target: clean – Cleans all unversioned files in project
clean:
	@git clean -dxf -e .vscode/


.PHONY: help
# target: help – Display all callable targets
help:
	@echo "Make targets in osparc-simcore:"
	@echo
	@egrep "^\s*#\s*target\s*:\s*" [Mm]akefile \
	| $(SED) -r "s/^\s*#\s*target\s*:\s*//g"
	@echo
