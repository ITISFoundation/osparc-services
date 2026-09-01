variable "DOCKER_REGISTRY" {
  default = "itisfoundation"
}

variable "SLEEPER_VERSION" {
  default = "latest"
}

target "_compression" {
    # zstd compresses better and faster than gzip for both size and (de)compression speed
    output = ["type=registry,compression=zstd,compression-level=3,force-compression=true,oci-mediatypes=true"]
}

target "sleeper" {
    inherits = ["_compression"]
    tags = ["${DOCKER_REGISTRY}/sleeper:latest","${DOCKER_REGISTRY}/sleeper:${SLEEPER_VERSION}"]
}

target "sleeper-gpu" {
    inherits = ["_compression"]
    tags = ["${DOCKER_REGISTRY}/sleeper-gpu:latest","${DOCKER_REGISTRY}/sleeper-gpu:${SLEEPER_VERSION}"]
}

target "sleeper-mpi" {
    inherits = ["_compression"]
    tags = ["${DOCKER_REGISTRY}/sleeper-mpi:latest","${DOCKER_REGISTRY}/sleeper-mpi:${SLEEPER_VERSION}"]
}
