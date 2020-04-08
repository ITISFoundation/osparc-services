#
# CONVENTIONS:
#
# - targets shall be ordered such that help list rensembles a typical workflow, e.g. 'make devenv tests'
# - add doc to relevant targets
# - internal targets shall start with '.'
# - KISS
#
# author: Sylvain Anderegg and Pedro Crespo

SHELL = /bin/sh
.DEFAULT_GOAL := help

export VCS_URL:=$(shell git config --get remote.origin.url || echo unversioned)
export VCS_REF:=$(shell git rev-parse --short HEAD || echo unversioned)
export VCS_STATUS:=$(if $(shell git status -s || echo unversioned),'modified/untracked','clean')
export BUILD_DATE:=$(shell date -u +"%Y-%m-%dT%H:%M:%SZ")

export DOCKER_REGISTRY ?= itisfoundation
export DOCKER_IMAGE_NAME ?= osparc-python-runner
export DOCKER_IMAGE_TAG ?= $(shell cat VERSION)

export COMPOSE_INPUT_DIR := ./validation/input
export COMPOSE_OUTPUT_DIR := .tmp/output

APP_NAME := 3d-viewer


# ENVIRON ----------------------------------
.PHONY: devenv
.venv:
	python3 -m venv $@
	# upgrading package managers
	$@/bin/pip3 install --upgrade \
		pip \
		wheel \
		setuptools
	# tooling
	$@/bin/pip3 install pip-tools

requirements.txt: .venv requirements.in
	# freezes requirements
	$</bin/pip-compile --upgrade --build-isolation --output-file $@ $(word2, $^)

devenv: .venv requirements.txt ## create a python virtual environment with tools to dev, run and tests cookie-cutter
	# installing extra tools
	@$</bin/pip3 install -r  $(word 2,$^)
	# your dev environment contains
	@$</bin/pip3 list
	@echo "To activate the virtual environment, run 'source $</bin/activate'"





.PHONY: build rebuild
# target: build, rebuild: – Builds all service images. Use `rebuild` to build w/o cache.
build: .env
	${DOCKER_COMPOSE} -f docker-compose.yml build --parallel

rebuild: .env
	${DOCKER_COMPOSE} -f docker-compose.yml build --no-cache --parallel

.PHONY: build-devel
# target: build-devel: – Builds images of core services for development.
build-devel: .env
	${DOCKER_COMPOSE} -f docker-compose.yml -f docker-compose.devel.yml build --parallel

.PHONY: up up-devel down
# target: up-devel: – deploys service in devel mode together with minimal swarm-like environment
up: .env ## Starts service
	${DOCKER_COMPOSE} -f docker-compose.yml up

.stack-paraviewweb-devel.yml: .env docker-compose.yml docker-compose.devel.yml
	docker-compose --file docker-compose.yml --file docker-compose.devel.yml --log-level=ERROR config > $@

SWARM_STACK_NAME=paraviewweb

up-devel: .stack-paraviewweb-devel.yml	
	docker stack deploy --compose-file $< $(SWARM_STACK_NAME)

down:
	docker stack rm $(SWARM_STACK_NAME)

.PHONY: push push-version pull pull-latest
push*: ## Pushes the service images to ${DOCKER_REGISTRY}
	${DOCKER_COMPOSE} -f docker-compose.yml push

pull*: ### Pulls the service images from ${DOCKER_REGISTRY}
	${DOCKER_COMPOSE} -f docker-compose.yml pull


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

# MISCELANEOUS -----------------------------------
.PHONY: replay
replay: .cookiecutterrc ## re-applies cookiecutter
	# Replaying gh:ITISFoundation/cookiecutter-osparc-service ...
	@cookiecutter --no-input --overwrite-if-exists \
		--config-file=$< \
		--output-dir="$(abspath $(CURDIR)/..)" \
		"gh:ITISFoundation/cookiecutter-osparc-service"


.PHONY: help
help: ## this colorful help
	@echo "Recipes for '$(notdir $(CURDIR))':"
	@echo ""
	@awk --posix 'BEGIN {FS = ":.*?## "} /^[[:alpha:][:space:]_-]+:.*?## / {printf "\033[36m%-20s\033[0m %s\n", $$1, $$2}' $(MAKEFILE_LIST)
	@echo ""


.PHONY: clean clean-force
git_clean_args = -dxf -e .vscode/ -e .venv
clean: ## cleans all unversioned files in project and temp files create by this makefile
	# Cleaning unversioned
	@git clean -n $(git_clean_args)
	@echo -n "Are you sure? [y/N] " && read ans && [ $${ans:-N} = y ]
	@echo -n "$(shell whoami), are you REALLY sure? [y/N] " && read ans && [ $${ans:-N} = y ]
	@git clean $(git_clean_args)
