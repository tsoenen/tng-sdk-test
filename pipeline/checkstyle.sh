#!/bin/bash
set -e
docker run -i --rm --privileged --pid='host' -v /var/run/docker.sock:/var/run/docker.sock tng-sdk-test flake8 --max-line-length=128 --ignore=W605,E402 tangotest
