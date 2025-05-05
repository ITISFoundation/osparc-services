# Developer README

### To upgrade the prodution image (dy-sidecar)



##### preconditions:
The service name and the folder name must be identical.
Rename `servcies/dy-tissue-properties` to `services/tissue-properties`, because of `grep "io.simcore.key" services/dy-tissue-properties/docker-compose.yml`.

##### Create common folders
Create a dot-osparc folder: `mkdir -p .osparc/tissue-properties`


Copy the common files there:
```
cp .osparc/my-example-service/*.j2 .osparc/tissue-properties;
cp .osparc/my-example-service/Makefile .osparc/tissue-properties;
cp .osparc/my-example-service/docker-compose.overwrite.yml .osparc/tissue-properties;
```

Copy the Dockerfile to the dot-osparc folder:
```
cp services/tissue-properties/Dockerfile .osparc/tissue-properties
```


##### Tinkering
Manually go through `.osparc/tissue-properties/docker-compose.overwrite.yml`. Change the service name. Change the dockerfile path. Change the `BASE_IMAGE` and any other things

Manually change `paths-mapping` in the `.osparc/my-example-service/runtime.yml.j2` jinja2 template. Check in the old Dockerfile where the inputs, outputs and workspace ("state_paths") are expected. Hardcode those paths here.

Manually change the `Dockerfile` until all old sins are purged. 

##### Build and test

```
cd .osparc/tissue-properties
make build VERSION=1.0.3
```
We suggest to make a patch-version-upgrade (violating semantic versioning...) so the oSPARC UI/UX for upgrading the service is easy and nice.

If the image buils (--> `Manually change theDockerfile until all old sins are purged`), push it to osparc-master.speag.com to check. You can repedeatly push images that are new to the same remote docker image-tag:

```
docker image tag simcore/services/dynamic/tissue-properties:1.0.3 registry.osparc-master.speag.com/simcore/services/dynamic/tissue-properties:1.0.3
docker push registry.osparc-master.speag.com/simcore/services/dynamic/tissue-properties:1.0.3
```
