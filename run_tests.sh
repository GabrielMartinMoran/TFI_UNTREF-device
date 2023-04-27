#!/bin/bash

# exit when any command fails
set -e

# Run flake8
tput setaf 6; printf "Running flake8 for linting checking\n"
tput sgr0; python -m flake8 .
tput setaf 2; printf "OK!\n\n"

# Run tests

tput setaf 6; printf "Running tests\n"
tput sgr0; python -m pytest tests --cov=. --cov-config=.coveragerc
tput setaf 2; printf "OK!\n\n"