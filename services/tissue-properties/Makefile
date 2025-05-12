
SHELL := /bin/bash
REPO_BASE_DIR := $(abspath $(dir $(abspath $(lastword $(MAKEFILE_LIST))))../../..)
CUR_TARGET := $(notdir $(CURDIR))

.PHONY: help
help: ## this help
	@echo "usage: make [target] ..."
	@echo ""
	@echo "Targets for '$(notdir $(CURDIR))':"
	@echo ""
	@awk 'BEGIN {FS = ":.*?## "}; /^[^.[:space:]].*?:.*?## / {if ($$1 != "help" && NF == 2) {printf "\033[36m%-20s\033[0m %s\n", $$1, $$2}}' $(MAKEFILE_LIST)
	@echo ""
DOCKER_IMAGE_NAME ?= $(notdir $(CURDIR))
.PHONY: docker-compose.yml
docker-compose.yml: ## runs ooil to assemble the docker-compose.yml file
	@echo "----- <ooil output> -----"
	@docker run -it --rm -v $(CURDIR):/mnt \
		-u $(shell id -u):$(shell id -g) \
		itisfoundation/ci-service-integration-library:v2.0.9-dev \
		bash -c "cd /mnt && ooil compose --metadata /mnt/.osparc --to-spec-file /mnt/docker-compose.yml"
	@echo "----- </ooil output> -----"

.PHONY: docker-compose.dev.yml
docker-compose.dev.yml: ## runs ooil to assemble the docker-compose.yml file
	@cd $(REPO_BASE_DIR) && $(VENV_BIN)/ooil compose --metadata .osparc --to-spec-file $(REPO_BASE_DIR)/docker-compose.dev.yml

.PHONY: build
build: | metadata.yml docker-compose.yml	## build docker image
	@docker compose --file $(REPO_BASE_DIR)/docker-compose.yml build $(DOCKER_IMAGE_NAME)

.PHONY: run-local
run-local: | build-dev docker-compose.yml ## runs images with local configuration
	@cd $(REPO_BASE_DIR) && docker compose --env-file $(REPO_BASE_DIR)/.osparc/$(DOCKER_IMAGE_NAME)/.env --file docker-compose.yml --file .osparc/$(DOCKER_IMAGE_NAME)/docker-compose.local.yml up --remove-orphans --force-recreate $(DOCKER_IMAGE_NAME)

.PHONY: build-dev
build-dev: | venv metadata.yml install docker-compose.dev.yml ## build dev docker image
	docker compose --env-file $(REPO_BASE_DIR)/.osparc/$(DOCKER_IMAGE_NAME)/.env --file $(REPO_BASE_DIR)/docker-compose.dev.yml --file $(REPO_BASE_DIR)/.osparc/$(DOCKER_IMAGE_NAME)/docker-compose.local.yml build $(DOCKER_IMAGE_NAME)
