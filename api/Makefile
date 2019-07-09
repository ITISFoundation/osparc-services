VENV:=$(abspath ${CURDIR}/../.venv)


# This will output the help for each task
# thanks to https://marmelab.com/blog/2016/02/29/auto-documented-makefile.html
.PHONY: help

help: ## this help
	@awk 'BEGIN {FS = ":.*?## "} /^[a-zA-Z_-]+:.*?## / {printf "\033[36m%-20s\033[0m %s\n", $$1, $$2}' $(MAKEFILE_LIST)

.DEFAULT_GOAL := help

${VENV}:
	python3 -m venv ${VENV}

.PHONY: install
install: ${VENV} ## install virtualenv and python
	${VENV}/bin/pip install --upgrade pip
	${VENV}/bin/pip install openapi-spec-validator

.PHONY: test
test: ## tests openapi specs schema against OAS 3.0.0
	${VENV}/bin/openapi-spec-validator --schema=3.0.0 ${CURDIR}/services_api.yaml
