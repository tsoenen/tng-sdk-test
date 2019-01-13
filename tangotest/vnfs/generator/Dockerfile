FROM ubuntu:xenial
MAINTAINER askhat.nuriddinov@ugent.be

RUN export DEBIAN_FRONTEND=noninteractive && apt-get update && apt-get install -y -q \
	net-tools \
	iproute \
	curl \
	netcat \
	netrw \
	socat \
	python-scapy

# set entry point for emulator gatekeeper
ENV SON_EMU_CMD "echo Traffic generator started"

# normal entry point
CMD /bin/bash
