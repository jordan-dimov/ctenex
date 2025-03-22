#!/bin/bash
set -e
echo "Installing project..."
poetry install -v
echo "Running tests..."
make test
echo "Tests completed successfully"
echo "Coverage report..."
make coverage
