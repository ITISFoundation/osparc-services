# Github CI

The Github continuous integration tool is used.

## Github configuration

The following Environment variables shall be set up to allow automatic deployment to Dockerhub.

```console
DOCKER_REGISTRY # this variable shall be set to your personal Dockerhub registry (typically equals username)
DOCKER_USERNAME = %your username%
DOCKER_PASSWORD = %your password%
```

> **Note:** On the main Github CI the DOCKER_REGISTRY variable is set to **itisfoundation**. All the built docker images are then deployed to itisfoundation/%imageName%.

## Release workflow

![release workflow](mermaid-diagram-20190827131033.svg)

