# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [2.5.1] - 2023-03-05
### Fixed
- Better logging for model reloading

## [2.5.0] - 2023-03-05
### Fixed
- Availability and ETA queries were mission partition on
- Skip training for stations with only one class
- Optimized dtypes for queries

### Added
- Allow for arbitrary code post processing to queries results on training

## [2.4.0] - 2023-03-01
### Added
- Bettter interface for experimenting and tracking on MLFlow
- Log query time to MLFlow

## [2.3.0] - 2023-02-28
### Added
- Allow to modify availability positive class weight

## [2.2.0] - 2023-02-28
### Added
- Compress models on upload

## [2.1.0] - 2023-02-28
### Added
- Persist models versions used for predictions in db

## [2.0.0] - 2023-02-28
### Changed
- Modify negative class weight for availability

## [1.0.5] - 2023-02-27
### Fixed
- Metaestimator predict proba bug

## [1.0.4] - 2023-02-27
### Fixed
- Metaestimator had no probability prediction

## [1.0.3] - 2023-02-27
### Fixed
- Allow dependency predictor to return probabilities

## [1.0.2] - 2023-02-27
### Fixed
- Refresh models every hour

## [1.0.1] - 2023-02-27
### Fixed
- Prediction returns numerical instead of array

## [1.0.0] - 2023-02-27
### Changed
- Python version constrained below 3.11

### Added
- ETA model training
- Availability model training
- Loading models from MLFlow in API
- Predict with loaded models in API
- Reading dataset from MinIO through DuckDB

### Removed
- Mocked predictions in API

### Fixed
- Stations were refreshed only once

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
