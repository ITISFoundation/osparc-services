# opencor

OpenCOR is a cross-platform modelling environment, which can be used to organise, edit, simulate and analy

## Usage

```console
$ make help

$ make devenv
$ source .venv/bin/activate

(.venv)$ make build
(.venv)$ make info-build
(.venv)$ make tests
```

## Workflow

1. The source code shall be copied to the [src](opencor/src/opencor) folder.
1. The [Dockerfile](opencor/src/Dockerfile) shall be modified to compile the source code.
2. The [metadata](opencor/metadata) yaml file shall be modified to at least accomodate with the expected inputs/outputs of the service.
3. The [execute](opencor/service.cli/execute) shell script shall be modified to run the service using the expected inputs and retrieve the expected outputs.
4. The test input/output shall be copied to [validation](opencor/validation).
5. The service docker image may be built and tested as ``make build tests`` (see usage above)

## Versioning

Two versions:

- integration version (e.g. [src/opencor/VERSION_INTEGRATION]) is updated with ``make version-integration-*``
- service version (e.g. [src/opencor/VERSION]) is updated with ``make version-service-*``

## CI/CD Integration

### Gitlab

add the following in your __gitlab-ci.yml__ file:

```yaml
include:
  - local: '/services/opencor/ci/gitlab-ci.yml'
```
