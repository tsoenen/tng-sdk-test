FROM ubuntu:xenial
MAINTAINER askhat.nuriddinov@ugent.be

# define interface names (should be the same as in VNFD)
ENV IFIN input
ENV IFOUT output

RUN export DEBIAN_FRONTEND=noninteractive && apt-get update && apt-get install -y -q \
	net-tools \
	iproute \
	inetutils-ping \
	iptables \
	arptables \
	ebtables \
	bridge-utils \
	ethtool \
	tshark

ADD start.sh start.sh
RUN chmod +x start.sh

# set entry point for emulator gatekeeper
ENV SON_EMU_CMD ./start.sh

# normal entry point
CMD /bin/bash
