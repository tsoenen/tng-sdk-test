#!/bin/bash
set -e

# Build vim-emu docker image
if [[ -d vim-emu ]]; then
    cd ./vim-emu
    git pull
else
    git clone https://osm.etsi.org/gerrit/osm/vim-emu.git
    cd ./vim-emu
fi

docker build -t vim-emu-test .

cd ../
docker build -t tng-sdk-test .
