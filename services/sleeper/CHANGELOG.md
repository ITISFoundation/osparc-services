# Changelog
All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [Unreleased]


## [2.3.0] - 2026-09-01
### Changed
- Uses Python 3.14, provisioned via `uv` (no more apt `python3`/`pip`)
- `uv` installed via distroless image copy, pinned to `0.12.8`
- Bumped GPU/MPI base image to `nvidia/cuda:13.3.1-base-ubuntu26.04`, now multi-arch (amd64+arm64)
- Registry pushes use zstd compression and OCI image labels/annotations
- Entrypoint ownership fixup now uses `fdfind` instead of `find`
- Version bumping now uses `bump-my-version` with TOML config (replaces `bump2version`/`.cfg`)
### Removed
- Legacy plain `docker tag`/`docker push` publish path and `linux/arm/v7` target

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
