# HELPER Makefile that countains all the recipe that will be used by every services. Please include it in your Makefile if you add a new service
SHELL := /bin/bash
REPO_BASE_DIR := $(abspath $(dir $(abspath $(lastword $(MAKEFILE_LIST))))..)
CUR_TARGET := $(notdir $(CURDIR))

# Check that given variables are set and all have non-empty values,
# die with an error otherwise.
#
# Params:
#   1. Variable name(s) to test.
#   2. (optional) Error message to print.
guard-%:
	@ if [ "${${*}}" = "" ]; then \
		echo "Argument '$*' is missing. TIP: make <rule> $*=<value>"; \
		exit 1; \
	fi

#
# Automatic VENV management
#
# Inspired from https://potyarkin.com/posts/2019/manage-python-virtual-environment-from-your-makefile/
DOCKER_IMAGE_NAME ?= $(notdir $(CURDIR))
VENVDIR=$(REPO_BASE_DIR)/.venv
VENV_BIN=$(VENVDIR)/bin
UV := $$HOME/.local/bin/uv
$(UV):
	@if [ ! -f $@ ]; then \
		echo "Installing uv..."; \
		curl -LsSf https://astral.sh/uv/install.sh | sh; \
	fi

# Use venv for any target that requires virtual environment to be created and configured
venv: $(VENVDIR)  ## configure repo's virtual environment
$(VENV_BIN): $(VENVDIR)

$(VENVDIR): $(UV)
	@if [ ! -d $@ ]; then \
		$< venv $@; \
		VIRTUAL_ENV=$@ $< pip install --quiet -r ${REPO_BASE_DIR}/requirements/devenv.txt; \
		$(VENV_BIN)/pre-commit install > /dev/null 2>&1; \
	fi
	-@$(UV) self --quiet update


$(VENV_BIN)/%: $(VENVDIR)
	@if [ ! -f "$@" ]; then \
		echo "ERROR: '$*' is not found in $(VENV_BIN)"; \
		exit 1; \
	fi

.PHONY: show-venv
show-venv: venv  ## show venv info
	@$(VENV_BIN)/python -c "import sys; print('Python ' + sys.version.replace('\n',''))"
	@$(UV) --version
	@echo venv: $(VENVDIR)

.PHONY: install
install: ${REPO_BASE_DIR}/requirements/devenv.txt venv
	@VIRTUAL_ENV=$(VENVDIR) $(UV) pip install --requirement $<

#
# HELPERS
#
MAKE_C := $(MAKE) --no-print-directory --directory

.PHONY: clean check_clean
clean: .check_clean ## Cleans all outputs
	# cleaning unversioned files in $(CURDIR)
	@git clean -dxf

.check_clean:
	@echo -n "Are you sure? [y/N] " && read ans && [ $${ans:-N} = y ]
	@echo -n "$(shell whoami), are you REALLY sure? [y/N] " && read ans && [ $${ans:-N} = y ]

# Helpers -------------------------------------------------
# NOTE: be careful that GNU Make replaces newlines with space which is why this command cannot work using a Make function
define upgrader
	@$(REPO_BASE_DIR)/scripts/classic_upgrader.py $(1) $(2) $(3) $(4) > $(5) 
endef

metadata.yml: metadata.yml.j2 guard-VERSION venv ## Create metadata.yml file
	# generate $@
	$(call upgrader, $<, $(REPO_BASE_DIR)/services/$(DOCKER_IMAGE_NAME)/docker-compose.yml,$(DOCKER_IMAGE_NAME),$(VERSION),$@)

runtime.yml: runtime.yml.j2 guard-VERSION venv ## Create metadata.yml file
	# generate $@
	$(call upgrader, $<, $(REPO_BASE_DIR)/services/$(DOCKER_IMAGE_NAME)/docker-compose.yml,$(DOCKER_IMAGE_NAME),$(VERSION),$@)


.PHONY: help
help: ## this help
	@echo "usage: make [target] ..."
	@echo ""
	@echo "Targets for '$(notdir $(CURDIR))':"
	@echo ""
	@awk 'BEGIN {FS = ":.*?## "}; /^[^.[:space:]].*?:.*?## / {if ($$1 != "help" && NF == 2) {printf "\033[36m%-20s\033[0m %s\n", $$1, $$2}}' $(MAKEFILE_LIST)
	@echo ""

.PHONY: docker-compose.yml
docker-compose.yml: guard-VERSION ## runs ooil to assemble the docker-compose.yml file
	@echo "----- <ooil output> -----"
	@docker run -it --rm -v $(REPO_BASE_DIR):/mnt \
		-u $(shell id -u):$(shell id -g) \
		itisfoundation/ci-service-integration-library:v2.0.9-dev \
		bash -c "cd /mnt && ooil compose --metadata /mnt/.osparc --to-spec-file /mnt/docker-compose.yml"
	@echo "----- </ooil output> -----"

.PHONY: build
build: | metadata.yml runtime.yml docker-compose.yml	## build docker image
	@docker compose --file $(REPO_BASE_DIR)/docker-compose.yml build $(DOCKER_IMAGE_NAME)
