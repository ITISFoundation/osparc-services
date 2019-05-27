VERSION := $(shell cat /proc/version)
# SAN this is a hack so that docker-compose works in the linux virtual environment under Windows
ifneq (,$(findstring Microsoft,$(VERSION)))
# executing from bash
$(echo 'detected WSL')
export DOCKER_COMPOSE=docker-compose
export DOCKER=docker
else ifeq ($(OS), Windows_NT)
$(echo 'detected Powershell/CMD')
# executing from powershell
export DOCKER_COMPOSE=docker-compose.exe
export DOCKER=docker.exe
else
$(echo 'detected native linux')
export DOCKER_COMPOSE=docker-compose
export DOCKER=docker
endif


# using ?= will only set if absent
export DOCKER_IMAGE_TAG ?= $(shell cat VERSION)
$(info DOCKER_IMAGE_TAG set to ${DOCKER_IMAGE_TAG})

# default to local (no registry)
export DOCKER_REGISTRY ?= itisfoundation
$(info DOCKER_REGISTRY set to ${DOCKER_REGISTRY})

export VCS_URL:=$(shell git config --get remote.origin.url)
export VCS_REF:=$(shell git rev-parse --short HEAD)
export BUILD_DATE:=$(shell date -u +"%Y-%m-%dT%H:%M:%SZ")

export BASE_IMAGE:=${DOCKER_REGISTRY}/jupyter-base-notebook:${DOCKER_IMAGE_TAG}

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
build: .env
	${DOCKER_COMPOSE} -f docker-compose.yml build --parallel

rebuild: .env
	${DOCKER_COMPOSE} -f docker-compose.yml build --no-cache --parallel

.PHONY: build-devel
# target: build-devel: – Builds images of core services for development.
build-devel: .env
	${DOCKER_COMPOSE} -f docker-compose.yml -f docker-compose.devel.yml build --parallel

.PHONY: up up-devel down
# target: up, down: – starts/stops service
# target: up-devel: – deploys service in devel mode together with minimal swarm-like environment
up:
	${DOCKER_COMPOSE} -f docker-compose.yml up

up-devel:
	${DOCKER_COMPOSE} -f docker-compose.yml -f docker-compose.devel.yml up

down:
	${DOCKER_COMPOSE} -f docker-compose.yml down
	${DOCKER_COMPOSE} -f docker-compose.yml -f docker-compose.devel.yml down

.PHONY: push
# target: push – Pushes the the service images to ${DOCKER_REGISTRY}
push: .env
	${DOCKER} login ${DOCKER_REGISTRY}
	${DOCKER_COMPOSE} -f docker-compose.yml push

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

## -------------------------------
# Virtual Environments
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
