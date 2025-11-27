#!/bin/sh
set -e
PYTEST_ARGS=${1:-}
pytest -q $PYTEST_ARGS
