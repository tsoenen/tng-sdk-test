#!/bin/bash
set -e
docker run -i --rm --privileged --pid='host' -v /var/run/docker.sock:/var/run/docker.sock tng-sdk-test pytest -vvv tests/test_instance.py::test_get_ip
