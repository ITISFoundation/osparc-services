# ans-model-viewer

ANS model viewer

## Usage

```console
$ make help

$ make build
$ make info-build
$ make tests
```

## Workflow

1. The source code shall be copied to the [src](ans-model-viewer/src/ans_model_viewer) folder.
2. The [Dockerfile](ans-model-viewer/src/Dockerfile) shall be modified to compile the source code.
3. The [.osparc](.osparc) is the configuration folder and source of truth for metadata: describes service info and expected inputs/outputs of the service.
4. The [execute](ans-model-viewer/service.cli/execute) shell script shall be modified to run the service using the expected inputs and retrieve the expected outputs.
5. The test input/output shall be copied to [validation](ans-model-viewer/validation).
6. The service docker image may be built and tested as ``make build tests`` (see usage above)
7. Optional: if your code requires specific CPU/RAM resources, edit [runtime.yml](.osparc/runtime.yml). In doubt, leave it as default.

## Have an issue or question?
Please open an issue [in this repository](https://github.com/ITISFoundation/cookiecutter-osparc-service/issues/).
---
<p align="center">
<image src="https://github.com/ITISFoundation/osparc-simcore-python-client/blob/4e8b18494f3191d55f6692a6a605818aeeb83f95/docs/_media/mwl.png" alt="Made with love at www.z43.swiss" width="20%" />
</p>
