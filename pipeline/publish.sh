#!/bin/bash
set -e
docker tag tng-sdk-test registry.sonata-nfv.eu:5000/tng-sdk-test:latest
docker tag tng-sdk-test sonatanfv/tng-sdk-test:latest

docker push registry.sonata-nfv.eu:5000/tng-sdk-test:latest
docker push sonatanfv/tng-sdk-test:latest
