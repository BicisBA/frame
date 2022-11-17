# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [0.6.0] - 2022-11-17
### Added
- S3 client to transparently handle minio/s3

## [0.5.2] - 2022-11-16
### Fixed
- Retries on data fetching

## [0.5.1] - 2022-11-12
### Fixed
- SQLite connection

## [0.5.0] - 2022-11-08
### Added
- Allow configuration of db pool size

## [0.4.5] - 2022-10-11
### Fixed
- Logging through Uvicorn
- Station ids as integers from the API fetch

### Changed
- Updating stations info and status with the stations service
- Namespaces for OpenAPI

### Added
- CLI command to run the server

## [0.4.4] - 2022-10-11
### Fixed
- Avoid integrity errors on stations status update
- Single commit for better throughput on stations and status update

## [0.4.3] - 2022-10-11
### Changed
- OpenAPI description and title

## [0.4.2] - 2022-10-11
### Fixed
- Postgres dialect fix

## [0.4.1] - 2022-10-09
### Fixed
- Updating db with the latest info from the db

## [0.4.0] - 2022-10-09
### Added
- Mocked predictions endpoint

## [0.3.0] - 2022-10-08
### Added
- Stations' status endpoint
- Replica of EcoBici's endpoints to avoid issuing too many queries
- On startup and periodic querying to the EcoBici API to fetch latest data

## [0.2.0] - 2022-09-25
### Added
- EcoBici stations models

## [0.1.0] - 2022-09-16
### Added
- Initial structure for the repo
