#!/bin/bash

# Usage:

set -e

# curl -I -X GET -H "Accept: application/json" -H "Portus-Auth: ${API_USER}:${API_TOKEN}" "https://${DOCKER_REGISTRY}/api/v1/users"
RESPONSE=$(curl -s -o /dev/null -w "%{http_code}" -X GET -H "Accept: application/json" -H "Portus-Auth: ${API_USER}:${API_TOKEN}" "https://${DOCKER_REGISTRY}/api/v1/users")
if [ "$RESPONSE" == "200" ]; then
    echo "portus is reachable"
    exit 0
else
    echo "portus not available"
    exit 1
fi
