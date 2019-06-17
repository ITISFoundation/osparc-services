# mattward-dash - How to Bake your Cookie

MattWard-Dash

## Development

1. The source code shall be copied to the [src](mattward-dash/src/mattward-dash) folder.
2. The [Dockerfile](mattward-dash/src/Dockerfile) shall be modified to compile the source code.
3. The [labels](mattward-dash/docker/labels) json files shall be modified to at least accomodate with the expected inputs/outputs of the service.
4. The [execute](mattward-dash/service.cli/execute) bash script shall be modified to run the service using the expected inputs and retrieve the expected outputs and log.
5. The test input/output/log shall be copied to [validation](mattward-dash/validation).
6. The service docker image may be built and tested using:

``` console
make .venv
source .venv/bin/activate

(.venv)$ make build
(.venv)$ make unit-test
(.venv)$ make integration-test
```

## Usage

Default usage will build the service inside a docker container and then run the service using the validation data as input by default.
Results will be stored in mattward-dash/tmp/output and logs in mattward-dash/tmp/log.

```console
make .venv
source .venv/bin/activate

(.venv)$ make build
(.venv)$ make up
```

## CI/CD Integration

### Gitlab

add the following in your __gitlab-ci.yml__ file:

```yaml
include:
  - local: '/services/mattward-dash/CI/gitlab-ci.yml'
```
