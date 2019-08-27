# osparc-services

Collection of some open-source services for the osparc simcore platform:

<!-- NOTE: when branched replace `master` in urls -->
[`master`](https://github.com/itisfoundation/osparc-services/tree/master)
[![Requirements Status](https://requires.io/github/ITISFoundation/osparc-services/requirements.svg?branch=master)](https://requires.io/github/ITISFoundation/osparc-services/requirements/?branch=master)
[![Build Status](https://travis-ci.com/ITISFoundation/osparc-services.svg?branch=master)](https://travis-ci.com/ITISFoundation/osparc-services)


## Continuous integration

[Continuous integration](ops/README.md)






<!-- TOC_BEGIN -->
<!-- Automaticaly produced by scripts/auto-doc/create-toc.py on 2019-08-27T07:33:53Z -->
## Available services [18]
|                                   name                                    |                                  description                                  |   type    |                                                                                                            latest version                                                                                                            |
|---------------------------------------------------------------------------|-------------------------------------------------------------------------------|-----------|--------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------|
|  [cc-0d-viewer](services/dy-2Dgraph/use-cases/cc)                         |  Graph viewer for data generated by cc-0d solver                              |  dynamic  |  [![](https://images.microbadger.com/badges/version/itisfoundation/cc-0d-viewer:2.10.0.svg)](https://microbadger.com/images/itisfoundation/cc-0d-viewer:2.10.0 'Get your own version badge on microbadger.com')                      |
|  [cc-1d-viewer](services/dy-2Dgraph/use-cases/cc)                         |  Graph viewer for data generated by cc-1d solver                              |  dynamic  |  [![](https://images.microbadger.com/badges/version/itisfoundation/cc-1d-viewer:2.10.0.svg)](https://microbadger.com/images/itisfoundation/cc-1d-viewer:2.10.0 'Get your own version badge on microbadger.com')                      |
|  [cc-2d-viewer](services/dy-2Dgraph/use-cases/cc)                         |  Graph viewer for data generated by cc-2d solver                              |  dynamic  |  [![](https://images.microbadger.com/badges/version/itisfoundation/cc-2d-viewer:2.10.0.svg)](https://microbadger.com/images/itisfoundation/cc-2d-viewer:2.10.0 'Get your own version badge on microbadger.com')                      |
|  [0D cardiac model viewer](services/dy-dash/cc-rabbit-0d/src)             |  Graph viewer for data generated by Rabbit SS and Human GB 0D cardiac models  |  dynamic  |  [![](https://images.microbadger.com/badges/version/itisfoundation/cc-0d-viewer:3.0.4.svg)](https://microbadger.com/images/itisfoundation/cc-0d-viewer:3.0.4 'Get your own version badge on microbadger.com')                        |
|  [1D cardiac model viewer](services/dy-dash/cc-rabbit-1d/src)             |  Graph viewer for data generated by Rabbit SS and Human GB 1D cardiac models  |  dynamic  |  [![](https://images.microbadger.com/badges/version/itisfoundation/cc-1d-viewer:3.0.3.svg)](https://microbadger.com/images/itisfoundation/cc-1d-viewer:3.0.3 'Get your own version badge on microbadger.com')                        |
|  [2D cardiac model viewer](services/dy-dash/cc-rabbit-2d/src)             |  Graph viewer for data generated by Rabbit SS and Human GB 2D cardiac models  |  dynamic  |  [![](https://images.microbadger.com/badges/version/itisfoundation/cc-2d-viewer:3.0.3.svg)](https://microbadger.com/images/itisfoundation/cc-2d-viewer:3.0.3 'Get your own version badge on microbadger.com')                        |
|  [jupyter-base-notebook](services/dy-jupyter/services/dy-jupyter)         |  Jupyter notebook                                                             |  dynamic  |  [![](https://images.microbadger.com/badges/version/itisfoundation/jupyter-base-notebook:2.13.0.svg)](https://microbadger.com/images/itisfoundation/jupyter-base-notebook:2.13.0 'Get your own version badge on microbadger.com')    |
|  [jupyter-neuron](services/dy-jupyter-extensions/neuron/)                 |  Jupyter notebook with preinstalled neuron modules                            |  dynamic  |  [![](https://images.microbadger.com/badges/version/itisfoundation/jupyter-neuron:1.1.0.svg)](https://microbadger.com/images/itisfoundation/jupyter-neuron:1.1.0 'Get your own version badge on microbadger.com')                    |
|  [jupyter-r-notebook](services/dy-jupyter/services/dy-jupyter)            |  Jupyter R notebook                                                           |  dynamic  |  [![](https://images.microbadger.com/badges/version/itisfoundation/jupyter-r-notebook:2.13.0.svg)](https://microbadger.com/images/itisfoundation/jupyter-r-notebook:2.13.0 'Get your own version badge on microbadger.com')          |
|  [jupyter-scipy-notebook](services/dy-jupyter/services/dy-jupyter)        |  Jupyter scipy notebook                                                       |  dynamic  |  [![](https://images.microbadger.com/badges/version/itisfoundation/jupyter-scipy-notebook:2.13.0.svg)](https://microbadger.com/images/itisfoundation/jupyter-scipy-notebook:2.13.0 'Get your own version badge on microbadger.com')  |
|  [kember-viewer](services/dy-2Dgraph/use-cases/kember)                    |  Graph viewer for data generated by kember solver                             |  dynamic  |  [![](https://images.microbadger.com/badges/version/itisfoundation/kember-viewer:2.10.0.svg)](https://microbadger.com/images/itisfoundation/kember-viewer:2.10.0 'Get your own version badge on microbadger.com')                    |
|  [mattward-viewer](services/dy-2Dgraph/use-cases/mattward)                |  Graph viewer for data generated by mattward solver                           |  dynamic  |  [![](https://images.microbadger.com/badges/version/itisfoundation/mattward-viewer:2.10.0.svg)](https://microbadger.com/images/itisfoundation/mattward-viewer:2.10.0 'Get your own version badge on microbadger.com')                |
|  [mattward-viewer](services/dy-dash/mattward-dash/src)                    |  Graph viewer for data generated by mattward solver                           |  dynamic  |  [![](https://images.microbadger.com/badges/version/itisfoundation/mattward-viewer:3.0.3.svg)](https://microbadger.com/images/itisfoundation/mattward-viewer:3.0.3 'Get your own version badge on microbadger.com')                  |
|  [2D plot](services/dy-raw-graphs/services/dy-raw-graphs)                 |  2D plots powered by RAW Graphs                                               |  dynamic  |  [![](https://images.microbadger.com/badges/version/itisfoundation/raw-graphs:2.10.4.svg)](https://microbadger.com/images/itisfoundation/raw-graphs:2.10.4 'Get your own version badge on microbadger.com')                          |
|  [Table view](services/dy-raw-graphs/services/dy-raw-graphs)              |  Table view powered by RAW Graphs                                             |  dynamic  |  [![](https://images.microbadger.com/badges/version/itisfoundation/raw-graphs-table:2.10.4.svg)](https://microbadger.com/images/itisfoundation/raw-graphs-table:2.10.4 'Get your own version badge on microbadger.com')              |
|  [modeler](services/dy-modeling/services/dy-modeling/server)              |  Modeler viewer                                                               |  dynamic  |  [![](https://images.microbadger.com/badges/version/itisfoundation/modeler-webserver:0.1.1.svg)](https://microbadger.com/images/itisfoundation/modeler-webserver:0.1.1 'Get your own version badge on microbadger.com')              |
|  [3d-viewer](services/dy-3dvis/services/dy-3dvis/simcoreparaviewweb)      |  Paraview Web-based Visualizer                                                |  dynamic  |  [![](https://images.microbadger.com/badges/version/itisfoundation/3d-viewer:2.11.0.svg)](https://microbadger.com/images/itisfoundation/3d-viewer:2.11.0 'Get your own version badge on microbadger.com')                            |
|  [3d-viewer-gpu](services/dy-3dvis/services/dy-3dvis/simcoreparaviewweb)  |  Paraview Web-based Visualizer GPU accelerated                                |  dynamic  |  [![](https://images.microbadger.com/badges/version/itisfoundation/3d-viewer-gpu:2.11.0.svg)](https://microbadger.com/images/itisfoundation/3d-viewer-gpu:2.11.0 'Get your own version badge on microbadger.com')                    |
*Updated on 2019-08-27T07:33:53Z*

<!-- TOC_END -->














