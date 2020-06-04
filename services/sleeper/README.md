# sleeper

A service which awaits for time to pass used for system validation.
Before waiting a payload function is run. This function may contain code which must be run
on a specific type of resource, example GPU.
It is also possible to make this service fail after it finishes all its activity,
as a final step.

## Usage

```console
$ make help

$ make devenv
$ . .venv/bin/activate

(.venv)$ make build
(.venv)$ make info-build
(.venv)$ make tests
```

## Workflow

1. The source code shall be copied to the [src](sleeper/src/sleeper) folder.
1. The [Dockerfile](sleeper/src/Dockerfile) shall be modified to compile the source code.
2. The [metadata](sleeper/metadata) yaml file shall be modified to at least accomodate with the expected inputs/outputs of the service.
3. The [execute](sleeper/service.cli/execute) shell script shall be modified to run the service using the expected inputs and retrieve the expected outputs.
4. The test input/output shall be copied to [validation](sleeper/validation).
5. The service docker image may be built and tested as ``make build tests`` (see usage above)

## Versioning

Two versions:

- integration version (e.g. [src/sleeper/VERSION_INTEGRATION]) is updated with ``make version-integration-*``
- service version (e.g. [src/sleeper/VERSION]) is updated with ``make version-service-*``

