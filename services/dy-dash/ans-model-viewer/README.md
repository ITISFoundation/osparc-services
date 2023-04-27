# SAN and VM model viewer

Interactive graph viewer for the Sinoatrial Model Viewer (san-model) and Ventricular Myocardium model viewer (vm-model) provided by UC Davis. 

## Usage

To build and test locally:

1. Open terminal and do:
    ```console
    $ make help
    $ make build
    $ make run-local-san (or make run-local-vm)
    ```
2. Open url http://0.0.0.0:8888/ to display the graph

Additionally, it can be tested in a local deployment of o²S²PARC by pushing it to the local registry with `publish-local`.

## How it works
The graphs are created using plotly-dash, all the logic is in the [app.py](../ans-model-viewer/src/ans_model_viewer/app.py) file. When the app is launched:
1. It checks if ".txt" files are provided in the two input ports
2. If inputs are provided, it checks the filename to choose which plotting functions to use (thanks to python multispatch library)
3. Display the plots using dash/plotly

To ensure that plots get updated when the input changes, the [Dash Interval Component](https://dash.plotly.com/live-updates) is used, that performs the steps above every 5 seconds.

## Additional information
The service was used using the [cookiecutter-osparc-service](https://github.com/ITISFoundation/cookiecutter-osparc-service/) with adaption for dynamic services taken from [jupyter-mah](https://github.com/ITISFoundation/jupyter-math).

## Have an issue or question?
Please open an issue [in this repository](https://github.com/ITISFoundation/cookiecutter-osparc-service/issues/).
---
<p align="center">
<image src="https://github.com/ITISFoundation/osparc-simcore-python-client/blob/4e8b18494f3191d55f6692a6a605818aeeb83f95/docs/_media/mwl.png" alt="Made with love at www.z43.swiss" width="20%" />
</p>
