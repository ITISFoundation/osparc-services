# dy-dash

This service contains several sub-services for displaying interactive services in a meaningful way such as 2D/3D graphs. It demonstrates the usage of the simcore-sdk package together with plotly-dash to create reproducible ways of displaying data. Depending on the use-cases the dash apps are enhanced with packages such as pandas to show how easy one can post-process data.

## Overview

### Commons

For each use-case a dash-based service is created that will:

1. Pull the information about the node ports configuration from the simcore database when needed in the dash app
2. Pull one or more input files in the service file system from the previous node(s) when needed in the dash app
3. Parse some data file using the python pandas package (such as comma-separated values)
4. Display the data using dash/plotly packages

### basic demo usage

1. rename _services/dy-dash/use-cases/.env-devel_ to _.env_
2. open terminal and do
    ```bash
    make build-devel
    make up-devel
    ```
3. open url [localhost:1238](localhost:1238) to see mattward use case
