#
# CONVENTIONS:
#
# - targets shall be ordered such that help list rensembles a typical workflow, e.g. 'make devenv tests'
# - add doc to relevant targets
# - internal targets shall start with '.'
# - KISS
#
# author: Katie Zhuang

SHELL = /bin/sh
.DEFAULT_GOAL := help

export VCS_URL:=$(shell git config --get remote.origin.url || echo unversioned)
export VCS_REF:=$(shell git rev-parse --short HEAD || echo unversioned)
export VCS_STATUS:=$(if $(shell git status -s || echo unversioned),'modified/untracked','clean')
export BUILD_DATE:=$(shell date -u +"%Y-%m-%dT%H:%M:%SZ")

export DOCKER_REGISTRY ?= itisfoundation
export DOCKER_IMAGE_NAME ?= pmr_mrg
export DOCKER_IMAGE_TAG ?= $(shell cat VERSION)

export COMPOSE_INPUT_DIR := ./validation/input
export COMPOSE_OUTPUT_DIR := .tmp/output

APP_NAME := pmr_mrg

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



# INTEGRATION -----------------------------------
metatada = metadata/metadata.yml
service.cli/run: $(metatada)
	# Updates adapter script from metadata in $<
	@.venv/bin/python3 tools/run_creator.py --metadata $< --runscript $@

docker-compose-meta.yml: $(metatada)
	# Injects metadata from $< as labels
	@.venv/bin/python3 tools/update_compose_labels.py --compose $@ --metadata $<

define _docker_compose_build
export DOCKER_BUILD_TARGET=$(if $(findstring -devel,$@),development,$(if $(findstring -cache,$@),cache,production)); \
$(if $(findstring -x,$@),\
	docker buildx > /dev/null; export DOCKER_CLI_EXPERIMENTAL=enabled; docker buildx bake  --file docker-compose-build.yml --file docker-compose-meta.yml $(if $(findstring -nc,$@),--no-cache,);,\
	$(if $(findstring -kit,$@),export DOCKER_BUILDKIT=1;export COMPOSE_DOCKER_CLI_BUILD=1;,) \
	docker-compose --file docker-compose-build.yml --file docker-compose-meta.yml build $(if $(findstring -nc,$@),--no-cache,) --parallel;\
)
endef



# DOCKER ----------------------------------- 
.PHONY: build build-devel build-kit-devel build-x build-devel-x
build build-devel build-kit build-kit-devel build-x build-devel-x: docker-compose-build.yml docker-compose-meta.yml service.cli/run ## builds images, -devel in development mode, -kit using docker buildkit, -x using docker buildX (if installed)
	# building image local/${DOCKER_IMAGE_NAME}...
	@$(call _docker_compose_build)

define show-meta
	$(foreach iid,$(shell docker images */$(1):* -q | sort | uniq),\
		docker image inspect $(iid) | jq '.[0] | .RepoTags, .ContainerConfig.Labels, .Config.Labels';)
endef

info-build: ## displays info on the built image
	# Built images
	@docker images */$(DOCKER_IMAGE_NAME):*
	# Tags and labels
	@$(call show-meta,$(DOCKER_IMAGE_NAME))



# TESTS----------------------------------- 
.PHONY: tests tests-unit tests-integration
tests-unit tests-integration: ## runs integration and unit tests
	@.venv/bin/pytest -vv \
		--basetemp=$(CURDIR)/tmp \
		--exitfirst \
		--failed-first \
		--pdb \
		--junitxml=pytest_$(subst tests-,,$@)test.xml \
		$(CURDIR)/tests/$(subst tests-,,$@)

tests: tests-unit tests-integration ## runs unit and integration tests


# PUBLISHING ----------------------------------- 
define _bumpversion
	# upgrades as $(subst $(1),,$@) version, commits and tags
	@bump2version --verbose --list --config-file $(1) $(subst $(2),,$@)
endef

.PHONY: version-service-patch version-service-minor version-service-major
version-service-patch version-service-minor version-service-major: versioning/service.cfg ## kernel/service versioning as patch
	@$(call _bumpversion,$<,version-service-)

.PHONY: push push-force push-version push-latest pull-latest pull-version tag-latest tag-version
tag-latest tag-version:
	docker tag local/$(DOCKER_IMAGE_NAME):production $(DOCKER_REGISTRY)/$(DOCKER_IMAGE_NAME):$(if $(findstring version,$@),$(DOCKER_IMAGE_TAG),latest)

version_valid = $(shell test $$(echo $(DOCKER_IMAGE_TAG) | cut --fields=1 --delimiter=.) -gt 0 > /dev/null && echo "image version is valid")
version_exists = $(shell DOCKER_CLI_EXPERIMENTAL=enabled docker manifest inspect $(DOCKER_REGISTRY)/$(DOCKER_IMAGE_NAME):$(DOCKER_IMAGE_TAG) > /dev/null && echo "image already exists on $(DOCKER_REGISTRY)")
push push-force: ## pushes (resp. force) services to the registry if service not available in registry.
	@$(if $(findstring force,$@),,\
		$(if $(call version_valid),$(info version is valid), $(error $(DOCKER_IMAGE_TAG) is not a valid version (major>=1)))\
		$(if $(call version_exists),$(error $(DOCKER_REGISTRY)/$(DOCKER_IMAGE_NAME):$(DOCKER_IMAGE_TAG) already exists on $(DOCKER_REGISTRY)), $(info no version found on $(DOCKER_REGISTRY)))\
	)
	@$(MAKE) push-version;
	@$(MAKE) push-latest;

push-latest push-version: ## publish service to registry with latest/version tag
	# pushing '$(DOCKER_REGISTRY)/$(DOCKER_IMAGE_NAME):$(if $(findstring version,$@),$(DOCKER_IMAGE_TAG),latest)'...
	@$(MAKE) tag-$(subst push-,,$@)
	@docker push $(DOCKER_REGISTRY)/$(DOCKER_IMAGE_NAME):$(if $(findstring version,$@),$(DOCKER_IMAGE_TAG),latest)
	# pushed '$(DOCKER_REGISTRY)/$(DOCKER_IMAGE_NAME):$(if $(findstring version,$@),$(DOCKER_IMAGE_TAG),latest)'

pull-latest pull-version: ## pull service from registry
	@docker pull $(DOCKER_REGISTRY)/$(DOCKER_IMAGE_NAME):$(if $(findstring version,$@),$(DOCKER_IMAGE_TAG),latest)


.PHONY: version-integration-patch version-integration-minor version-integration-major
version-integration-patch version-integration-minor version-integration-major: versioning/integration.cfg ## integration versioning as patch (bug fixes not affecting API/handling), minor/major (backwards-compatible/INcompatible API changes)
	@$(call _bumpversion,$<,version-integration-)


# DEVELOPMENT ---------------------------------------- 
# NOTE: since using docker-compose would create the folders automatically but as root user, which is inconvenient
define _clean_output_dirs
	# cleaning output directory
	rm -rf $(COMPOSE_OUTPUT_DIR)/*
endef
$(COMPOSE_OUTPUT_DIR):
	@$(call _clean_output_dirs)
	mkdir -p $@
	# created output directory $(COMPOSE_OUTPUT_DIR)

docker-compose-configs = $(wildcard docker-compose.*yml)

.compose-production.yml .compose-development.yml: $(docker-compose-configs)
	# creating config for stack with 'local/$(DOCKER_IMAGE_NAME):$(patsubst .compose-%.yml,%,$@)' to $@
	@export DOCKER_REGISTRY=local; \
	export DOCKER_IMAGE_TAG=$(patsubst .compose-%.yml,%,$@); \
	docker-compose -f docker-compose.yml $(if $(findstring -development,$@), -f docker-compose.devel.yml,) --log-level=ERROR config > $@

define _docker_compose_cli
	$(eval docker_compose_path=.compose-$(if $(findstring devel,$@),development,production).yml)
	$(MAKE) $(docker_compose_path)
	@docker-compose -f $(docker_compose_path) $(1)
endef


.PHONY: down up up-devel shell shell-devel
up up-devel: $(COMPOSE_INPUT_DIR) $(COMPOSE_OUTPUT_DIR) down ## Starts the service for testing. Devel mode mounts the folders for direct development.
	# starting a service
	$(call _docker_compose_cli,up)

shell shell-devel: $(COMPOSE_INPUT_DIR) $(COMPOSE_OUTPUT_DIR) down ## Starts a shell instead of running the container. Useful for development.
	# starting service and go in...
	$(call _docker_compose_cli,run --service-ports $(APP_NAME) /bin/sh)

down: .compose-development.yml ## stops the service
	@docker-compose -f $< down



# MISCELANEOUS -----------------------------------
.PHONY: replay
replay: .cookiecutterrc ## re-applies cookiecutter
	# Replaying https://github.com/ITISFoundation/cookiecutter-osparc-service ...
	@cookiecutter --no-input --overwrite-if-exists \
		--config-file=$< \
		--output-dir="$(abspath $(CURDIR)/..)" \
		"https://github.com/ITISFoundation/cookiecutter-osparc-service"


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
