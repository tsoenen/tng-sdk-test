#  Copyright (c) 2015 SONATA-NFV, 5GTANGO
# ALL RIGHTS RESERVED.
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
#
# Neither the name of the SONATA-NFV, 5GTANGO
# nor the names of its contributors may be used to endorse or promote
# products derived from this software without specific prior written
# permission.
#
# This work has been performed in the framework of the SONATA project,
# funded by the European Commission under Grant number 671517 through
# the Horizon 2020 and 5G-PPP programmes. The authors would like to
# acknowledge the contributions of their colleagues of the SONATA
# partner consortium (www.sonata-nfv.eu).
#
# This work has also been performed in the framework of the 5GTANGO project,
# funded by the European Commission under Grant number 761493 through
# the Horizon 2020 and 5G-PPP programmes. The authors would like to
# acknowledge the contributions of their colleagues of the SONATA
# partner consortium (www.5gtango.eu).

import time
import tempfile
import docker


def build_probe(path, name=None):
    dockerfile_content = """
    FROM ubuntu:xenial
    RUN apt-get update -q && apt-get install -qy \
        apt-transport-https \
        ca-certificates \
        python-setuptools \
        python-dev \
        python-pip \
        git \
        libltdl-dev
    RUN pip install git+https://github.com/sonata-nfv/tng-sdk-test
    COPY . /
    ENV TANGOTEST_PLATFORM VNV
    CMD /bin/bash
    """

    dockerfile = tempfile.NamedTemporaryFile(bufsize=0)
    dockerfile.write(dockerfile_content)

    docker_client = docker.from_env()
    docker_image, _ = docker_client.images.build(path=path, dockerfile=dockerfile.name)

    tag = name or 'tng-sdk-test-{}'.format(time.strftime("%Y-%m-%d-%H-%M-%S"))
    docker_image.tag(tag)

    return tag
