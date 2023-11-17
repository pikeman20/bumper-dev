#!/bin/bash

# List of package names
packages=("aiodns" "aiohttp" "aiohttp-jinja2" "cachetools" "coloredlogs" "cryptography" "defusedxml" "gmqtt" "Jinja2" "passlib" "setuptools" "tinydb" "verboselogs" "websockets" "stevedore")

echo "" >requirements.txt
# Loop through the packages
for package in "${packages[@]}"; do
  # Get the latest version number using jq and curl
  latest_version=$(curl -s "https://pypi.org/pypi/${package}/json" | jq -r '.releases | keys | .[]' | sort -V | tail -n 1)
  # Print the formatted output
  echo "${package}==${latest_version}" >>requirements.txt
done

# ------------------------------------------------------------------------------

packages_dev=("mypy" "pre-commit" "pylint" "pytest" "pytest-aiohttp" "pytest-asyncio" "pytest-cov" "pytest-env" "pytest-timeout" "testfixtures" "types-cachetools" "types-setuptools")

echo "" >requirements-dev.txt
# Loop through the packages
for package in "${packages_dev[@]}"; do
  # Get the latest version number using jq and curl
  latest_version=$(curl -s "https://pypi.org/pypi/${package}/json" | jq -r '.releases | keys | .[]' | sort -V | tail -n 1)
  # Print the formatted output
  echo "${package}==${latest_version}" >>requirements-dev.txt
done
