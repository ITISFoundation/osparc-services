# Changelog
All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [Unreleased]

## [2.3.0] - 2026-09-01
### Added
- New "snore" input: emits random log lines at a rate (`1/s`) defined per second of sleep (disabled unless set)
- Prints actual available CPUs/memory at startup, and GPU/VRAM info (`nvidia-smi` output) once for `-gpu` (previously not surfaced, or repeated every sleep iteration)
### Changed
- Uses Python 3.14, provisioned via `uv` (no more apt `python3`/`pip`)
- `uv` installed via distroless image copy, pinned to `0.12.8`
- `-gpu`/`-mpi` variants now build from the same `python:${PYTHON_VERSION}-slim` image as the plain service (dropped `nvidia/cuda`): `nvidia-smi`/driver libs are injected by the NVIDIA Container Toolkit at runtime regardless of base image, and sleeper never links `cudart`/`cuBLAS` directly — this cuts the `-gpu`/`-mpi` image size by ~5x (~980MB → ~200MB)
- `make up`'s `docker-compose.yml` now sets `DOCKER_RESOURCE_VRAM`/`DOCKER_RESOURCE_MPI` for `-gpu`/`-mpi` and requests an actual `nvidia` GPU reservation for `-gpu`, so these variants exercise their resource-specific code paths locally instead of silently no-op'ing
- Registry pushes use zstd compression and OCI image labels/annotations
- Entrypoint ownership fixup now uses `fdfind` instead of `find`
- Version bumping now uses `bump-my-version` with native TOML config (`versioning/*.toml`, replaces `bump2version`/`.cfg`)
- `tools/run_creator.py`/`tools/update_compose_labels.py` are now self-contained `uv run --script` tools (no venv required)
- `make up`/`down`/`shell` now use `docker compose` (v2 plugin) instead of the deprecated `docker-compose` (v1) CLI
- Clearer runtime logs: "remaining sleep time" now has an explicit unit (`s`) and warns if snoring/payload leave no time left to sleep; walking to bed now reports remaining distance per step; added emojis throughout
### Removed
- Legacy plain `docker tag`/`docker push` publish path and `linux/arm/v7` target
- Deprecated `org.label-schema.*` labels (superseded by `org.opencontainers.image.*`)
### Fixed
- `-gpu`/`-mpi` containers failing to start on Ubuntu 26.04 base: pre-existing `ubuntu` user at uid 1000 collided with the host uid during entrypoint's `usermod` (moot since these variants no longer use an Ubuntu/CUDA base, see above)
- `-gpu`/`-mpi` containers failing with `python: Permission denied`: uv's standalone Python interpreter wasn't copied into the production image alongside the venv (moot for the same reason)
- `make up`/`down` failing with `empty compose file`: `docker compose config` doesn't support the (v1-only) `--log-level` flag

## [2.2.1] - 2024-03-08
### Changed
- Unit of the "dream" input/output is now byte


## [2.2.0] - 2024-02-27
### Added
- Option to have a dream defined in bytes
### Changed
- No more upper limit on the sleep interval
- Uses Python 3.11
- Uses `uv` for dependency management


## [2.1.6] - 2023-05-26
### Fixed
- Input limits


## [2.1.5] - 2023-05-16
### Fixed
- Progress not being flushed properly


## [2.1.4] - 2022-04-20
### Changed
- Inputs and Outputs follow new unit schema
### Added
- Constraint added to "Sleep interval" input


## [2.1.3] - 2021-12-10
### Added
- Sleeper now advertises the resources it needs


## [2.1.2] - 2021-12-09
### Added
- ARM support


## [2.1.1] - 2020-02-24
### Added
- Fourth input added, "Distance to bed" (meters). Before sleeping, it will walk this distance


## [2.1.0] - 2020-02-15
### Added
- Unit (seconds) field added to the input#2 and output#2


## [2.0.2] - 2020-08-05
### Added
- `sleeper-mpi` which emulates MPI services

### Changed
- changelog format
- bumped the version for `sleeper` and `sleeper-gpu` images
- `nidia/cuda:10.0-base` is now used, down from 10.2


## [2.0.1] - 2020-07-14
### Added
- changelog to project

### Fixed
- issue with print not formatting output properly
