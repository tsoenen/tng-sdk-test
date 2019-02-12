#!/bin/bash
set -e

cd ../
rm -rf vim-emu
rm -rf tng-sdk-test

docker image rm vim-emu-test:latest tng-sdk-test:latest
