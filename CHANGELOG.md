# Change Log

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](http://keepachangelog.com/)
and this project adheres to [Semantic Versioning](http://semver.org/).

## [Unreleased]

## [0.8.0] - 2022-08-14

### Changed
- package name from `mutwo.ext-isis` to `mutwo.isis`

### Added
- custom exception for better error handling


## [0.7.0] - 2022-02-20

### Changed
- `IsisConverter` to `EventToSingingSynthesis`
- `IsisScoreConverter` to `EventToIsisScore`


## [0.6.0] - 2022-02-15

### Added
- `isis_executable_path` parameter to `IsisConverter`

### Changed
- `ISIS_PATH` to `DEFAULT_ISIS_EXECUTABLE_PATH`
- location of `DEFAULT_ISIS_EXECUTABLE_PATH` from `constants` to `configurations`


## [0.5.0] - 2022-02-10

### Changed
- to namespace package to make it compatible with recent `mutwo.ext-core` and `mutwo.ext-music` versions


## [0.4.0] - 2022-01-15

### Added
- global constant XSAMPA in `isis_constants` which contains all supported phonemes


## [0.3.0] - 2022-01-12

### Changed
- applied movement from music related parameter and converter modules (which have been moved from [mutwo core](https://github.com/mutwo-org/mutwo) in version 0.49.0 to [mutwo.ext-music](https://github.com/mutwo-org/mutwo.ext-music))

