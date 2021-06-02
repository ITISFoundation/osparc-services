# dy-static-file-server

Dynamic service for testing purpose

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

1. The source code shall be copied to the [src](dy-static-file-server/src/dy_static-file-server) folder.
1. The [Dockerfile](dy-static-file-server/src/Dockerfile) shall be modified to compile the source code.
2. The [metadata](dy-static-file-server/metadata) yaml file shall be modified to at least accomodate with the expected inputs/outputs of the service.
3. The [execute](dy-static-file-server/service.cli/execute) shell script shall be modified to run the service using the expected inputs and retrieve the expected outputs.
4. The test input/output shall be copied to [validation](dy-static-file-server/validation).
5. The service docker image may be built and tested as ``make build tests`` (see usage above)

## Versioning

Two versions:

- integration version (e.g. [src/dy_static-file-server/VERSION_INTEGRATION]) is updated with ``make version-integration-*``
- service version (e.g. [src/dy_static-file-server/VERSION]) is updated with ``make version-service-*``

## CI/CD Integration

### Gitlab

add the following in your __gitlab-ci.yml__ file:

```yaml
include:
  - local: '/services/dy-static-file-server/ci/gitlab-ci.yml'
```
