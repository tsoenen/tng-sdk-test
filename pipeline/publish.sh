#!/bin/bash
set -e
docker tag tng-sdk-test registry.sonata-nfv.eu:5000/tng-sdk-test
docker push registry.sonata-nfv.eu:5000/tng-sdk-test
