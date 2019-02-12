#!/bin/bash
set -e

# Build vim-emu docker image
cd ..
git clone https://osm.etsi.org/gerrit/osm/vim-emu.git
cd ./vim-emu
docker build -t vim-emu-test .

cd ../tng-sdk-test
docker build -t tng-sdk-test .
