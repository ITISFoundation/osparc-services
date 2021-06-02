#!/bin/bash
set -o errexit
set -o nounset
set -o pipefail
IFS=$'\n\t'

# Usage:    export API_USER=theportususer
#           export API_TOKEN=xfdlkjfslkj
#           export DOCKER_REGISTRY=registry.com
#           export DOCKER_PROJECT=path/to/image
#           delete-image-from-regitry-portus



cd "$(dirname "$0")"

echo "deleting ${DOCKER_REGISTRY}/${DOCKER_PROJECT}"
ID=$(curl --request GET --header 'Accept: application/json' --header "Portus-Auth: ${API_USER}:${API_TOKEN}" https://"${DOCKER_REGISTRY}"/api/v1/repositories | jq -r --arg DOCKER_PROJECT "${DOCKER_PROJECT}" 'map(select(.full_name == $DOCKER_PROJECT))'[0].id)
if [ "$ID" == "null" ]; then
    echo "no repository found, not doing anything"
    exit 1
fi
echo "deleting repository with id: $ID"
curl --request DELETE --header 'Accept: application/json' --header "Portus-Auth: ${API_USER}:${API_TOKEN}" "https://${DOCKER_REGISTRY}/api/v1/repositories/${ID}"
echo "deleting done"
