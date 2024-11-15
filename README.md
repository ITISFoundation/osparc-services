# osparc-services

Collection of some open-source services for the osparc simcore platform:

<!-- NOTE: when branched replace `master` in urls -->
[`master`](https://github.com/itisfoundation/osparc-services/tree/master)
[![Requirements Status](https://requires.io/github/ITISFoundation/osparc-services/requirements.svg?branch=master)](https://requires.io/github/ITISFoundation/osparc-services/requirements/?branch=master)


## Continuous integration

[Continuous integration](ci/README.md)
<!-- TOC_BEGIN -->
<!-- Automaticaly produced by scripts/auto-doc/create-toc.py on 2024-11-15T10:33:51Z -->
## Available services [27]
|                                                      name                                                       |                                                                                                                                                                                                                                                                                                                                                                  description                                                                                                                                                                                                                                                                                                                                                                   |      type       |                                                                                                                         latest version                                                                                                                         |                                                             build status                                                              |
|  -------------------------------------------------------------------------------------------------------------  |  --------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------  |  -------------  |  ------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------  |  -----------------------------------------------------------------------------------------------------------------------------------  |
|  [3d-viewer](services/dy-3dvis/docker/custom/Dockerfile)                                                        |  Paraview Web-based Visualizer                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                 |  dynamic        |  [![](https://images.microbadger.com/badges/version/itisfoundation/3d-viewer:3.0.3.svg)](https://microbadger.com/images/itisfoundation/3d-viewer:3.0.3 'See Image Version')                                                                                    |                                                                                                                                       |
|  [3d-viewer-gpu](services/dy-3dvis/docker/custom/Dockerfile)                                                    |  Paraview Web-based Visualizer                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                 |  dynamic        |  [![](https://images.microbadger.com/badges/version/itisfoundation/3d-viewer-gpu:3.0.3.svg)](https://microbadger.com/images/itisfoundation/3d-viewer-gpu:3.0.3 'See Image Version')                                                                            |                                                                                                                                       |
|  [cardiac_myocyte_grandi](services/ma-myocyteele/docker/custom/Dockerfile)                                      |  This is the mouse cardiac myocyte electrophysiology model from Eleonora Grandi at UC Davis.                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                   |  computational  |  [![](https://images.microbadger.com/badges/version/itisfoundation/cardiac_myocyte_grandi:1.0.1.svg)](https://microbadger.com/images/itisfoundation/cardiac_myocyte_grandi:1.0.1 'See Image Version')                                                          |                                                                                                                                       |
|  [0D cardiac model viewer](services/dy-dash/cc-rabbit-0d/src/Dockerfile)                                        |  Graph viewer for data generated by Rabbit SS and Human GB 0D cardiac models                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                   |  dynamic        |  [![](https://images.microbadger.com/badges/version/itisfoundation/cc-0d-viewer:3.0.4.svg)](https://microbadger.com/images/itisfoundation/cc-0d-viewer:3.0.4 'See Image Version')                                                                              |  ![0D cardiac model viewer](https://github.com/ITISFoundation/osparc-services/workflows/cc-0d-viewer/badge.svg?branch=master)         |
|  [1D cardiac model viewer](services/dy-dash/cc-rabbit-1d/src/Dockerfile)                                        |  Graph viewer for data generated by Rabbit SS and Human GB 1D cardiac models                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                   |  dynamic        |  [![](https://images.microbadger.com/badges/version/itisfoundation/cc-1d-viewer:3.0.4.svg)](https://microbadger.com/images/itisfoundation/cc-1d-viewer:3.0.4 'See Image Version')                                                                              |  ![1D cardiac model viewer](https://github.com/ITISFoundation/osparc-services/workflows/cc-1d-viewer/badge.svg?branch=master)         |
|  [2D cardiac model viewer](services/dy-dash/cc-rabbit-2d/src/Dockerfile)                                        |  Graph viewer for data generated by Rabbit SS and Human GB 2D cardiac models                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                   |  dynamic        |  [![](https://images.microbadger.com/badges/version/itisfoundation/cc-2d-viewer:3.0.5.svg)](https://microbadger.com/images/itisfoundation/cc-2d-viewer:3.0.5 'See Image Version')                                                                              |  ![2D cardiac model viewer](https://github.com/ITISFoundation/osparc-services/workflows/cc-2d-viewer/badge.svg?branch=master)         |
|  [CSV Table viewer](services/dy-csv-table/Dockerfile)                                                           |  CSV Table viewer powered by [csv-to-html-table](https://github.com/derekeder/csv-to-html-table)                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                               |  dynamic        |  [![](https://images.microbadger.com/badges/version/itisfoundation/csv-table:1.0.0.svg)](https://microbadger.com/images/itisfoundation/csv-table:1.0.0 'See Image Version')                                                                                    |  ![CSV Table viewer](https://github.com/ITISFoundation/osparc-services/workflows/dy-csv-table/badge.svg?branch=master)                |
|  [dy-static-file-server](services/dy-static-file-server/docker/custom/Dockerfile)                               |  Legacy test dynamic service (starts using original director-v0). The /workdir/generated-data directory is populated if no content is present.                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                 |  dynamic        |  [![](https://images.microbadger.com/badges/version/itisfoundation/dy-static-file-server:2.0.7.svg)](https://microbadger.com/images/itisfoundation/dy-static-file-server:2.0.7 'See Image Version')                                                            |  ![dy-static-file-server](https://github.com/ITISFoundation/osparc-services/workflows/dy-static-file-server/badge.svg?branch=master)  |
|  [dy-static-file-server-dynamic-sidecar](services/dy-static-file-server/docker/custom/Dockerfile)               |  Modern test dynamic service (with dynamic sidecar). Changes to the inputs will be forwarded to the outputs. The /workdir/generated-data directory is populated if no content is present.                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                      |  dynamic        |  [![](https://images.microbadger.com/badges/version/itisfoundation/dy-static-file-server-dynamic-sidecar:2.0.7.svg)](https://microbadger.com/images/itisfoundation/dy-static-file-server-dynamic-sidecar:2.0.7 'See Image Version')                            |                                                                                                                                       |
|  [dy-static-file-server-dynamic-sidecar-compose-spec](services/dy-static-file-server/docker/custom/Dockerfile)  |  Modern test dynamic service providing a docker-compose specification file (with dynamic sidecar and compose-spec). Changes to the inputs will be forwarded to the outputs. The /workdir/generated-data directory is populated if no content is present.                                                                                                                                                                                                                                                                                                                                                                                                                                                                                       |  dynamic        |  [![](https://images.microbadger.com/badges/version/itisfoundation/dy-static-file-server-dynamic-sidecar-compose-spec:2.0.7.svg)](https://microbadger.com/images/itisfoundation/dy-static-file-server-dynamic-sidecar-compose-spec:2.0.7 'See Image Version')  |                                                                                                                                       |
|  [jupyter-base-notebook](services/dy-jupyter/Dockerfile)                                                        |  Jupyter notebook                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                              |  dynamic        |  [![](https://images.microbadger.com/badges/version/itisfoundation/jupyter-base-notebook:2.14.0.svg)](https://microbadger.com/images/itisfoundation/jupyter-base-notebook:2.14.0 'See Image Version')                                                          |                                                                                                                                       |
|  [jupyter-neuron](services/dy-jupyter-extensions/neuron/Dockerfile)                                             |  Jupyter notebook with preinstalled neuron modules                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                             |  dynamic        |  [![](https://images.microbadger.com/badges/version/itisfoundation/jupyter-neuron:1.1.0.svg)](https://microbadger.com/images/itisfoundation/jupyter-neuron:1.1.0 'See Image Version')                                                                          |                                                                                                                                       |
|  [jupyter-r-notebook](services/dy-jupyter/Dockerfile)                                                           |  Jupyter R notebook                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                            |  dynamic        |  [![](https://images.microbadger.com/badges/version/itisfoundation/jupyter-r-notebook:2.14.0.svg)](https://microbadger.com/images/itisfoundation/jupyter-r-notebook:2.14.0 'See Image Version')                                                                |                                                                                                                                       |
|  [jupyter-scipy-notebook](services/dy-jupyter/Dockerfile)                                                       |  Jupyter scipy notebook                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                        |  dynamic        |  [![](https://images.microbadger.com/badges/version/itisfoundation/jupyter-scipy-notebook:2.14.0.svg)](https://microbadger.com/images/itisfoundation/jupyter-scipy-notebook:2.14.0 'See Image Version')                                                        |                                                                                                                                       |
|  [kember-viewer](services/dy-2Dgraph/use-cases/kember/Dockerfile)                                               |  Graph viewer for data generated by kember solver                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                              |  dynamic        |  [![](https://images.microbadger.com/badges/version/itisfoundation/kember-viewer:2.14.0.svg)](https://microbadger.com/images/itisfoundation/kember-viewer:2.14.0 'See Image Version')                                                                          |                                                                                                                                       |
|  [Mapcore Flatmap](services/dy-mapcore-widget/Dockerfile)                                                       |  Interactive maps reveal the anatomy and functional relationships of the autonomic nerves and the organs that they innervate. 2D and 3D maps render spatial dynamics, connectivity, and physiology across a range of species and nerve-organ systems.                                                                                                                                                                                                                                                                                                                                                                                                                                                                                          |  dynamic        |  [![](https://images.microbadger.com/badges/version/itisfoundation/mapcore-widget:0.1.24.svg)](https://microbadger.com/images/itisfoundation/mapcore-widget:0.1.24 'See Image Version')                                                                        |  ![Mapcore Flatmap](https://github.com/ITISFoundation/osparc-services/workflows/dy-mapcore-widget/badge.svg?branch=master)            |
|  [mattward-viewer](services/dy-dash/mattward-dash/src/Dockerfile)                                               |  Graph viewer for data generated by mattward solver                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                            |  dynamic        |  [![](https://images.microbadger.com/badges/version/itisfoundation/mattward-viewer:3.0.5.svg)](https://microbadger.com/images/itisfoundation/mattward-viewer:3.0.5 'See Image Version')                                                                        |  ![mattward-viewer](https://github.com/ITISFoundation/osparc-services/workflows/mattward-viewer/badge.svg?branch=master)              |
|  [OpenCOR](services/oc-opencor-base/docker/custom/Dockerfile)                                                   |  OpenCOR is a cross-platform modelling environment, which can be used to organise, edit, simulate and analyse CellML and SED-ML files.                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                         |  computational  |  [![](https://images.microbadger.com/badges/version/itisfoundation/opencor:1.0.4.svg)](https://microbadger.com/images/itisfoundation/opencor:1.0.4 'See Image Version')                                                                                        |  ![OpenCOR](https://github.com/ITISFoundation/osparc-services/workflows/oc-opencor-base/badge.svg?branch=master)                      |
|  [opencorservice_demo](services/oc-guytonmodel/docker/ubuntu/Dockerfile)                                        |  opencorservice_demo                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                           |  computational  |  [![](https://images.microbadger.com/badges/version/itisfoundation/opencorservice_demo:1.0.1.svg)](https://microbadger.com/images/itisfoundation/opencorservice_demo:1.0.1 'See Image Version')                                                                |                                                                                                                                       |
|  [pmr_mrg](services/oc-pmrmrg/docker/ubuntu/Dockerfile)                                                         |  Creates a simulation of the MRG fiber based on the model found on the PMR https://models.physiomeproject.org/e/5f7/mcintyre_richardson_grill_model_2001.cellml/view                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                           |  computational  |  [![](https://images.microbadger.com/badges/version/itisfoundation/pmr_mrg:1.0.2.svg)](https://microbadger.com/images/itisfoundation/pmr_mrg:1.0.2 'See Image Version')                                                                                        |                                                                                                                                       |
|  [2D plot](services/dy-raw-graphs/Dockerfile)                                                                   |  2D plots powered by RAW Graphs                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                |  dynamic        |  [![](https://images.microbadger.com/badges/version/itisfoundation/raw-graphs:2.11.1.svg)](https://microbadger.com/images/itisfoundation/raw-graphs:2.11.1 'See Image Version')                                                                                |                                                                                                                                       |
|  [Table view](services/dy-raw-graphs/Dockerfile)                                                                |  Table view powered by RAW Graphs                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                              |  dynamic        |  [![](https://images.microbadger.com/badges/version/itisfoundation/raw-graphs-table:2.11.1.svg)](https://microbadger.com/images/itisfoundation/raw-graphs-table:2.11.1 'See Image Version')                                                                    |                                                                                                                                       |
|  [modeler](services/dy-modeling/server/Dockerfile)                                                              |  Modeler viewer                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                |  dynamic        |  [![](https://images.microbadger.com/badges/version/itisfoundation/modeler-webserver:0.1.1.svg)](https://microbadger.com/images/itisfoundation/modeler-webserver:0.1.1 'See Image Version')                                                                    |                                                                                                                                       |
|  [sleeper](services/sleeper/docker/custom/Dockerfile)                                                           |  A service which awaits for time to pass, two times.                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                           |  computational  |  [![](https://images.microbadger.com/badges/version/itisfoundation/sleeper:2.2.1.svg)](https://microbadger.com/images/itisfoundation/sleeper:2.2.1 'See Image Version')                                                                                        |  ![sleeper](https://github.com/ITISFoundation/osparc-services/workflows/sleeper/badge.svg?branch=master)                              |
|  [sleeper-gpu](services/sleeper/docker/custom/Dockerfile)                                                       |  A service which awaits for time to pass, two times.                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                           |  computational  |  [![](https://images.microbadger.com/badges/version/itisfoundation/sleeper-gpu:2.2.1.svg)](https://microbadger.com/images/itisfoundation/sleeper-gpu:2.2.1 'See Image Version')                                                                                |                                                                                                                                       |
|  [sleeper-mpi](services/sleeper/docker/custom/Dockerfile)                                                       |  A service which awaits for time to pass, two times.                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                           |  computational  |  [![](https://images.microbadger.com/badges/version/itisfoundation/sleeper-mpi:2.2.1.svg)](https://microbadger.com/images/itisfoundation/sleeper-mpi:2.2.1 'See Image Version')                                                                                |                                                                                                                                       |
|  [Tissue properties](services/dy-tissue-properties/Dockerfile)                                                  |  Tissue properties compiled in an extensive, critical literature review by the ITIS Foundation. Visit [itis.swiss/database](https://itis.swiss/database) for additional information, e.g., on tissue parameter variability/uncertainty, quality assurance, and the explored sources. Please use the following citation when referring to the database: Hasgall PA, Di Gennaro F, Baumgartner C, Neufeld E, Lloyd B, Gosselin MC, Payne D, Klingenböck A, Kuster N, ITIS Database for thermal and electromagnetic parameters of biological tissues, Version 4.0, May 15, 2018, DOI: 10.13099/VIP21000-04-0. [itis.swiss/database](https://itis.swiss/database). Powered by [csv-to-html-table](https://github.com/derekeder/csv-to-html-table)  |  dynamic        |  [![](https://images.microbadger.com/badges/version/itisfoundation/tissue-properties:1.0.1.svg)](https://microbadger.com/images/itisfoundation/tissue-properties:1.0.1 'See Image Version')                                                                    |  ![Tissue properties](https://github.com/ITISFoundation/osparc-services/workflows/dy-tissue-properties/badge.svg?branch=master)       |
*Updated on 2024-11-15T10:33:51Z*

<!-- TOC_END -->

