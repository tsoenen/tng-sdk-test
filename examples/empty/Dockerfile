FROM ubuntu:xenial
MAINTAINER askhat.nuriddinov@ugent.be

RUN export DEBIAN_FRONTEND=noninteractive && apt-get update && apt-get install -y -q \
	net-tools \
	iproute

# set entry point for emulator gatekeeper
ENV SON_EMU_CMD "echo Started"

# normal entry point
CMD /bin/bash
