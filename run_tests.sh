#!/bin/bash -e

# get env vars for library paths, etc
source ./env.sh

# TODO this is a Sauce Labs standard that we may not need in the future
./version.sh

find . -name '*.pyc' -delete

nosetests
