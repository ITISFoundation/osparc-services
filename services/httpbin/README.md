# httpbin

The httpbin is wrapped as a dynamic service for testing and validation of the `dynamic-sidecar`

## Local development

Start the oSPARC stack with the local-registry (usually found at `registry:5000`).

The below command will build tag and push the containers to help with development

    make build transfer-to-local-registry


Inside the registry the following images will be pushed:

- simcore/services/dynamic/httpbin and exposed as `httpbin` to the user
- simcore/services/dynamic/httpbin-dynamic-sidecar and exposed as `httpbin-dynamic-sidecar` to the user
- simcore/services/dynamic/httpbin-dynamic-sidecar-compose and exposed as `httpbin-dynamic-sidecar-compose` to the user

After pushing the images permissions must be granted manually via adminer.


**Known limitations** 

Only `httpbin` will be exposed on `some.domain/x/UUID` becaus it will be stated as a **legacy dynamic service**.
The UI for this service dose not take into account the `/x/UUID` subpath.
