#!/bin/bash
set -e
docker run -it --rm --privileged --pid='host' -v /var/run/docker.sock:/var/run/docker.sock tng-sdk-test pytest -vvv tests
