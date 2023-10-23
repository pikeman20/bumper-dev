# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [Unreleased]

### Added

- conf files added
  - add this `CHANGELOG.md`
  - add `pyproject.toml`
  - add `create_cert.sh`
    - for create example cert for bumper
  - add `requirements-update.sh`
    - for fast create new `requirements.txt` and `requirements-dev.txt` with newest versions
  - add `.codecov.yml` and `.coveragerc`
  - add `.gitattributes`
  - .github adds
    - add `DISCUSSION_TEMPLATE`
    - add `ISSUE_TEMPLATE` as yaml and removed md one
    - add `PULL_REQUEST_TEMPLATE.md`
    - add workflow `release-drafter.yml`

### Changed

- conf files updates
  - renamed `.prettierrc` to `.prettierrc.yml` and rewrite in yaml
  - renamed `bandit.yaml` to `bandit.yml`
  - renamed `LICENSE.txt` to `LICENSE`
  - update `setup.cfg`
    - flake8 changed line length to 130
    - isort add line-length as 130
  - update version in `requirements.txt`
  - update version in `requirements-dev.txt`
  - add additional information into `README.md`
  - update additional in `pylintrc`
    - updated good-names
    - updated disable
    - updated max-parents
    - added max-args
  - updated `mypy.ini` to python version 3.11
  - update `Dockerfile`
    - update from versions as variables
    - add labels
    - changed to work with bumper updates
  - moved `docker-compose.yaml` and extend with additional configs
  - moved `ngnix.conf` into new folder configs/ngnix
  - update `.gitignore`
  - update `.yamllint`
  - update `.pre-commit-config.yaml`
    - version updates
    - additional args added
  - updated `CmdLine.md` by add sh to code block
  - .github updates
    - update workflow `ci.yml`
      - with new version, comments
      - update build step for docker build and push to ghcr.io
    - update workflow `codeql-analysis.yml`

### Removed

- conf files removed
  - `.dockerfile`
  - `requirements-test.txt`
  - removed `README.md` from data folder and add `.gitempty`
  - removed `README.md` from logs folder and add `.gitempty`
  - removed `README.md` from certs folder and add `.gitempty`
  - .github removes
    - remove `md` files from `ISSUE_TEMPLATE`, replaced with new `yaml` templates

[unreleased]: https://github.com/edenhaus/bumper/compare/dev...MVladislav:bumper:dev
