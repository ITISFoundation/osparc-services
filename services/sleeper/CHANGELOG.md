# Changelog
All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [Unreleased]


## [2.1.4] - 2022-04-20
### Changed
- Inputs and Outputs follow new unit schema
### Added
- Constraints added to inputs


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

