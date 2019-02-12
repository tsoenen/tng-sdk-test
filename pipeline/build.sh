#!/bin/bash
set -e

# Build vim-emu docker image
git clone https://osm.etsi.org/gerrit/osm/vim-emu.git
cd ./vim-emu
docker build -t vim-emu-test .

cd ../
docker build -t tng-sdk-test .
