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

import os
import docker
import requests

from tangotest.vim.base import BaseVIM, BaseInstance
from tangotest.tangotools.package_parser import parse_package


class Vnv(BaseVIM):
    @property
    def InstanceClass(self):
        return VnvInstance

    def add_instances_from_package(self, package, package_format='tango'):
        if not os.path.isfile(package):
            raise Exception('Package {} not found'.format(package))

        package_data = parse_package(package_format)

        instances = []
        for name, vdus in package_data.items():
            if len(vdus) != 1:
                raise Exception('Only one deployment unit per NF is supported.')
            interfaces = vdus.items()[0][1]
            instances.append(self._add_instance(name, interfaces))

        return instances

    def add_link(self, *args, **kwargs):
        raise Exception('Network configuration is not available')


class VnvInstance(DockerBasedInstance):
    """
    A representation of an instance on the V&V platform.
    Should not be created manually but by the Vnv class.
    """
    pass
