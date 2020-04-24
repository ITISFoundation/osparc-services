# opencorservice_demo

opencorservice_demo

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

1. The source code shall be copied to the [src](opencorservice_demo/src/opencorservice_demo) folder.
1. The [Dockerfile](opencorservice_demo/src/Dockerfile) shall be modified to compile the source code.
2. The [metadata](opencorservice_demo/metadata) yaml file shall be modified to at least accomodate with the expected inputs/outputs of the service.
3. The [execute](opencorservice_demo/service.cli/execute) shell script shall be modified to run the service using the expected inputs and retrieve the expected outputs.
4. The test input/output shall be copied to [validation](opencorservice_demo/validation).
5. The service docker image may be built and tested as ``make build tests`` (see usage above)

## Versioning

Two versions:

- integration version (e.g. [src/opencorservice_demo/VERSION_INTEGRATION]) is updated with ``make version-integration-*``
- service version (e.g. [src/opencorservice_demo/VERSION]) is updated with ``make version-service-*``

## CI/CD Integration

### Gitlab

add the following in your __gitlab-ci.yml__ file:

```yaml
include:
  - local: '/services/opencorservice_demo/ci/gitlab-ci.yml'
```
