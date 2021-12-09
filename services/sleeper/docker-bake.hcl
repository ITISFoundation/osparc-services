variable "DOCKER_REGISTRY" {
  default = "itisfoundation"
}

variable "SLEEPER_VERSION" {
  default = "latest"
}

target "sleeper" {
    tags = ["${DOCKER_REGISTRY}/volume-sync:latest","${DOCKER_REGISTRY}/volume-sync:${SLEEPER_VERSION}"]
    output = ["type=registry"]
}
