# cardiac_myocyte_grandi

This is the mouse cardiac myocyte electrophysiology model from Eleonora Grandi at UC Davis.

## Usage

```console
$ make help

$ make devenv
$ source .venv/bin/activate

(.venv)$ make build
(.venv)$ make info-build
(.venv)$ make tests
```

 Two versions:

- integration version (e.g. [src/ cardiac_myocyte_grandi/VERSION_INTEGRATION]) is updated with ``make version-integration-*``
- service version (e.g. [src/cardiac_myocyte_grandi/VERSION]) is updated with ``make version-service-*``
