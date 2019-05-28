# dy-2Dgraph

This service contains several sub-services for displaying data in a meaningful way such as with tables and 2D/3D graphs. It demonstrates the usage of the simcore-sdk package together with the well known jupyter notebook to create reproducible ways of displaying data. Depending on the use-cases the jupyter notebooks are enhanced with packages such as pandas, matplotlib and plotly to show how easy one can post-process data.

## Overview

### Commons

For each use-case a jupyter notebook-based service is created that will:

1. Pull the information about the node ports configuration from the simcore database when needed in the jupyter notebook
2. Pull one or more input files in the service file system from the previous node(s) when needed in the jupyter notebook
3. Parse some data file using the python pandas package (such as comma-separated values)
4. Display the data using python matplotlib/plotly packages

### basic demo usage

1. rename _services/dy-2Dgraph/use-cases/.env-devel_ to _.env_
2. open terminal and do
    ```bash
    make build-devel
    make up-devel
    ```
3. open url [localhost:1234](localhost:1234) to see 0d use case graphs
4. open url [localhost:1235](localhost:1235) to see 1d use case graphs
5. open url [localhost:1236](localhost:1236) to see 2d use case graphs
6. open url [localhost:9001](localhost:9001) to see the s3 file manager UI
7. open url [localhost:18080](localhost:18080) to see the adminer (db visualiser)
