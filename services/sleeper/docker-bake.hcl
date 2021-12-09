variable "DOCKER_REGISTRY" {
  default = "itisfoundation"
}

variable "SLEEPER_VERSION" {
  default = "latest"
}

target "sleeper" {
    tags = ["${DOCKER_REGISTRY}/sleeper:latest","${DOCKER_REGISTRY}/sleeper:${SLEEPER_VERSION}"]
    output = ["type=registry"]
}
