# pmr_mrg

Creates a simulation of the MRG fiber based on the model found on the PMR https://models.physiomeproject.org/e/5f7/mcintyre_richardson_grill_model_2001.cellml/view

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

- integration version (e.g. [src/opencorservice_demo/VERSION_INTEGRATION]) is updated with ``make version-integration-*``
- service version (e.g. [src/opencorservice_demo/VERSION]) is updated with ``make version-service-*``
