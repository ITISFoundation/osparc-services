#!/bin/bash
set -o errexit
set -o nounset
set -o pipefail
IFS=$'\n\t'

cd "$(dirname "$0")"

echo "deleting ${DOCKER_REGISTRY}/${DOCKER_PROJECT}"

DOCKER_TAG=$(./docker-registry-curl.bash https://"${DOCKER_REGISTRY}"/v2/"${DOCKER_PROJECT}"/tags/list | jq -r .tags[0])
while [ "${DOCKER_TAG}" != "null" ]
do
    echo "${DOCKER_PROJECT}:${DOCKER_TAG}..."
    DOCKER_ETAG=$(./docker-registry-curl.bash --head --header "Accept: application/vnd.docker.distribution.manifest.v2+json" -X GET "https://${DOCKER_REGISTRY}/v2/${DOCKER_PROJECT}/manifests/${DOCKER_TAG}" | grep --extended-regexp "Docker-Content-Digest: " | cut --delimiter=" " --fields=2 | tr --delete \" | sed 's/\r//')
    export DOCKER_ETAG
    ./docker-registry-curl.bash --request DELETE "https://${DOCKER_REGISTRY}/v2/${DOCKER_PROJECT}/manifests/${DOCKER_ETAG}"
    DOCKER_TAG=$(./docker-registry-curl.bash https://"${DOCKER_REGISTRY}"/v2/"${DOCKER_PROJECT}"/tags/list | jq -r .tags[0])
done

