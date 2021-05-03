# defaults
.DEFAULT_GOAL := help

# Use bash not sh
SHELL := /bin/bash


HTTPBIN_COMPOSE_FILE := httpbin_compose_spec.yaml

export LOCAL_REGISTRY:=registry:5000
export DOCKER_REGISTRY:=itisfoundation

export DOCKER_IMAGE_TAG=$(shell cat VERSION)

export VCS_URL:=$(shell git config --get remote.origin.url)
export VCS_REF:=$(shell git rev-parse --short HEAD)
export BUILD_DATE:=$(shell date -u +"%Y-%m-%dT%H:%M:%SZ")

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


define add_label
	@echo "Image	$(1)"
	@echo "Label	$(2)"
	@echo "Content	$(3)"
    echo "FROM $(1)" | docker build --label $(2)=$(3) -t "$(1)" -
endef


.PHONY: venv
venv: ## Creates a python virtual environment with tools for building
	python3 -m venv .venv
	.venv/bin/pip3 install --upgrade pip wheel setuptools
	.venv/bin/pip3 install yq
	@echo "To activate the venv, execute 'source .venv/bin/activate' or '.venv/bin/activate.bat' (WIN)"


.PHONY: build
build:	## builds and tags the images
	${DOCKER_COMPOSE} -f docker-compose.yml build
	$(call add_label,${DOCKER_REGISTRY}/httpbin-dynamic-sidecar-compose:${DOCKER_IMAGE_TAG},simcore.service.compose-spec,'$(shell cat ${HTTPBIN_COMPOSE_FILE} | yq -c -M)')

	@echo "Image Labels => ${DOCKER_REGISTRY}/httpbin:${DOCKER_IMAGE_TAG}"
	@docker inspect -f "{{json .Config.Labels }}" ${DOCKER_REGISTRY}/httpbin:${DOCKER_IMAGE_TAG}
	@echo "Image Labels => ${DOCKER_REGISTRY}/httpbin-dynamic-sidecar:${DOCKER_IMAGE_TAG}"
	@docker inspect -f "{{json .Config.Labels }}" ${DOCKER_REGISTRY}/httpbin-dynamic-sidecar:${DOCKER_IMAGE_TAG}
	@echo "Image Labels => ${DOCKER_REGISTRY}/httpbin-dynamic-sidecar-compose:${DOCKER_IMAGE_TAG}"
	@docker inspect -f "{{json .Config.Labels }}" ${DOCKER_REGISTRY}/httpbin-dynamic-sidecar-compose:${DOCKER_IMAGE_TAG}


.PHONY: transfer-to-local-registry
transfer-to-local-registry:	## transfers images to local registry
	@docker tag ${DOCKER_REGISTRY}/httpbin:${DOCKER_IMAGE_TAG} ${LOCAL_REGISTRY}/simcore/services/dynamic/httpbin:${DOCKER_IMAGE_TAG}
	@docker push ${LOCAL_REGISTRY}/simcore/services/dynamic/httpbin:${DOCKER_IMAGE_TAG}

	@docker tag ${DOCKER_REGISTRY}/httpbin-dynamic-sidecar:${DOCKER_IMAGE_TAG} ${LOCAL_REGISTRY}/simcore/services/dynamic/httpbin-dynamic-sidecar:${DOCKER_IMAGE_TAG}
	@docker push ${LOCAL_REGISTRY}/simcore/services/dynamic/httpbin-dynamic-sidecar:${DOCKER_IMAGE_TAG}

	@docker tag ${DOCKER_REGISTRY}/httpbin-dynamic-sidecar-compose:${DOCKER_IMAGE_TAG} ${LOCAL_REGISTRY}/simcore/services/dynamic/httpbin-dynamic-sidecar-compose:${DOCKER_IMAGE_TAG}
	@docker push ${LOCAL_REGISTRY}/simcore/services/dynamic/httpbin-dynamic-sidecar-compose:${DOCKER_IMAGE_TAG}

	@curl -s ${LOCAL_REGISTRY}/v2/_catalog | jq '.repositories'
	@curl -s http://${LOCAL_REGISTRY}/v2/simcore/services/dynamic/httpbin/tags/list?n=50 | jq '.'
	@curl -s http://${LOCAL_REGISTRY}/v2/simcore/services/dynamic/httpbin-dynamic-sidecar/tags/list?n=50 | jq '.'
	@curl -s http://${LOCAL_REGISTRY}/v2/simcore/services/dynamic/httpbin-dynamic-sidecar-compose/tags/list?n=50 | jq '.'

.PHONY: push
push:	## pushes existing images
	${DOCKER_COMPOSE} -f docker-compose.yml push

.PHONY: pull
pull:	## pulls existing images
	${DOCKER_COMPOSE} -f docker-compose.yml pull

.PHONY: test
test:	## runs tests
	@echo 'test passed, nothing validated here'

.PHONY: help
# thanks to https://marmelab.com/blog/2016/02/29/auto-documented-makefile.html
help:
	@echo "General help commands devel"
	@awk 'BEGIN {FS = ":.*?## "} /^[[:alpha:][:space:]_-]+:.*?## / {printf "\033[36m%-20s\033[0m %s\n", $$1, $$2}' $(MAKEFILE_LIST)
	@echo ""


