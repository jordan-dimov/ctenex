#! /bin/bash

echo "make lint"
make lint DIFF=1
if [ $? -ne 0 ]; then
    echo "Error: lint failed"
    exit 1
fi
echo "DONE!"

echo "make format"
make format DIFF=1
if [ $? -ne 0 ]; then
    echo "Error: format failed"
    exit 1
fi
echo "DONE!"

echo "make type-check"
make type-check
if [ $? -ne 0 ]; then
    echo "Error: type-check failed"
    exit 1
fi
echo "DONE!"
