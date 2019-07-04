# mattward-dash

MattWard-Dash

## Structure

- mattward-dash/
- mattward-dash/src
- mattward-dash/tests
- mattward-dash/validation

## Usage

Default usage will build the service inside a docker container and then run the service using the validation data as input by default.
Results will be stored in mattward-dash/tmp/output and logs in mattward-dash/tmp/log.

```console
# activate python virtual env
make .venv
source .venv/bin/activate

# to build the project
(.venv)$ make build
# to run the project with the validation data as input
(.venv)$ make up


# to run the test suites
(.venv)$ pip install -r tests/requirements.txt
(.venv)$ make unit-test
(.venv)$ make integration-test
```

## Versioning

Do the following to change the version of the dockerized service

```console
# activate python virtual env
make .venv
source .venv/bin/activate

(.venv)$ pip install bumpversion
(.venv)$ bumpversion ARG
```
