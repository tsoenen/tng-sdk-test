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
import requests

from mininet.node import RemoteController

from emuvim.cli.rest.compute import RestApiClient as EmuComputeClient
from emuvim.cli.rest.network import RestApiClient as EmuNetworkClient

from emuvim.dcemulator.net import DCNetwork
from emuvim.api.rest.rest_api_endpoint import RestApiEndpoint
from emuvim.api.sonata import SonataDummyGatekeeperEndpoint
from emuvim.api.tango import TangoLLCMEndpoint
from emuvim.api.tango.llcm import initialize_GK

from tangotest.vim.dockerbase import DockerBasedVIM, DockerBasedInstance
from tangotest.utils import get_free_tcp_port

from tangotest.tangotools.vnv_checker import (
    vnv_called_once,
    vnv_not_called,
    vnv_called_without_parameter,
    vnv_checker_start,
    vnv_checker_stop
)


class Emulator(DockerBasedVIM):
    """
    This class can be used to run tests on the VIM-EMU emulator.
    In order to use this class you need VIM-EMU to be installed locally.
    More information about VIM-EMU and installation instructions can be found on the project wiki-page:
    https://osm.etsi.org/wikipub/index.php/VIM_emulator

    Example:
        >>> from tangotest.vim.emulator import Emulator
        >>> vim = Emulator()
        >>> vim.start()
        >>> /* your code here */
        >>> vim.stop()

        You can also use this class with the context manager:

        >>> with Emulator() as vim:
        >>>      /* your code here */
    """

    def __init__(self, endpoint_port=None, tango_port=None, sonata_port=None,
                 enable_learning=False, vnv_checker=False, *args, **kwargs):
        """
        Initialize the Emulator.
        This method doesn't start the Emulator.

        Args:
            endpoint_port (int): vim-emu REST API port. Default: random free port
            tango_port (int): Sonata gatekeeper port. Default: random free port
            sonata_port (int): Tango gatekeeper port. Default: random free port
            vnv_checker (bool): Check if the code can be reused on the 5GTANGO V&V platform
            enable_learning (bool): Enable learning switch
        """
        super(Emulator, self).__init__(*args, **kwargs)
        self.endpoint_port = endpoint_port
        self.tango_port = tango_port
        self.sonata_port = sonata_port
        self.vnv_checker = vnv_checker
        self.enable_learning = enable_learning

    @property
    def InstanceClass(self):
        return EmulatorInstance

    @vnv_checker_start
    def start(self):
        """
        Run the Emulator and the endpoints.
        """
        super(Emulator, self).start()

        initialize_GK()

        self.net = DCNetwork(controller=RemoteController, monitor=False, enable_learning=self.enable_learning)
        self.datacenter = self.net.addDatacenter('dc1')

        endpoint_ip = '0.0.0.0'
        endpoint_port = self.endpoint_port or get_free_tcp_port()
        self.endpoint = 'http://{}:{}'.format(endpoint_ip, endpoint_port)

        self.rest_api = RestApiEndpoint(endpoint_ip, endpoint_port)
        self.rest_api.connectDCNetwork(self.net)
        self.rest_api.connectDatacenter(self.datacenter)
        self.rest_api.start()

        sonata_ip = '0.0.0.0'
        sonata_port = self.sonata_port or get_free_tcp_port()
        self.sonata_address = 'http://{}:{}'.format(sonata_ip, sonata_port)
        self.sonata_gatekeeper = SonataDummyGatekeeperEndpoint(sonata_ip, sonata_port)
        self.sonata_gatekeeper.connectDatacenter(self.datacenter)
        self.sonata_gatekeeper.start()

        tango_ip = '0.0.0.0'
        tango_port = self.tango_port or get_free_tcp_port()
        self.tango_address = 'http://{}:{}'.format(tango_ip, tango_port)
        self.tango_gatekeeper = TangoLLCMEndpoint(tango_ip, tango_port)
        self.tango_gatekeeper.connectDatacenter(self.datacenter)
        self.tango_gatekeeper.start()

        self.net.start()

    @vnv_checker_stop
    def stop(self):
        """
        Stop the Emulator and the endpoints.
        """
        self.rest_api.stop()
        self.net.stop()

        super(Emulator, self).stop()

    @vnv_called_once
    def add_instances_from_package(self, package, package_format='tango'):
        if not os.path.isfile(package):
            raise Exception('Package {} not found'.format(package))

        if package_format == 'tango':
            gatekeeper_address = self.tango_address
        elif package_format == 'sonata':
            gatekeeper_address = self.sonata_address
        else:
            raise Exception('package_format must be "tango" or "sonata", passed {}.'.format(package_format))

        # Upload the package
        with open(package, 'rb') as package_content:
            files = {'package': package_content}
            url = '{}/packages'.format(gatekeeper_address)
            response = requests.post(url, files=files)
            if not response.ok:
                raise Exception('Something went wrong during uploading.')

        # Instantiate the service
        url = '{}/instantiations'.format(gatekeeper_address)
        response = requests.post(url, data='{}')
        if not response.ok:
            raise Exception('Something went wrong during instantiation.')

        instances = []
        for name, instance in self.datacenter.containers.items():
            if name in self.instances:
                continue
            instances.append(self._add_instance(name))

        return instances

    @vnv_called_without_parameter('interfaces')
    def add_instance_from_image(self, name, image, interfaces=None, docker_command=None):
        """
        Run a Docker image on the Emulator.

        Args:
            name (str): The name of an instance
            image (str): The name of an image
            interfaces (int), (list) (str) or (dict): Network configuration
            docker_command (str): The command to execute when starting the instance

        Returns:
            (EmulatorInstance): The added instance
        """

        if not self._image_exists(image):
            raise Exception('Docker image {} not found'.format(image))

        if not interfaces:
            interfaces = '(id=emu0)'
        elif isinstance(interfaces, str):
            pass
        elif isinstance(interfaces, int):
            interfaces = ','.join(['(id=emu{})'.format(i) for i in range(interfaces)])
        elif isinstance(interfaces, list):
            interfaces = ','.join(['(id={})'.format(i) for i in interfaces])
        elif isinstance(interfaces, dict):
            interfaces = ','.join(['(id={},ip={})'.format(k, v) for k, v in interfaces.items()])
        else:
            raise Exception('Wrong network configuration: {}'.format(interfaces))

        params = {
            'name': name,
            'image': image,
            'command': docker_command,
            'network': interfaces,
            'endpoint': self.endpoint,
            'datacenter': 'dc1'
        }

        EmuComputeClient().start(params)

        return self._add_instance(name)

    @vnv_called_without_parameter('interfaces')
    def add_instance_from_source(self, name, path, interfaces=None, image_name=None,
                                 docker_command=None, **docker_build_args):
        """
        Build and run a Docker image on the Emulator.

        Args:
            name (str): The name of an instance
            path (str): The path to the directory containing Dockerfile
            interfaces (int), (list) (str) or (dict): Network configuration
            image_name (str): The name of an image. Default: tangotest<name>
            docker_command (str): The command to execute when starting the instance
            **docker_build_args: Extra arguments to be used by the Docker engine to build the image

        Returns:
            (EmulatorInstance): The added instance
        """
        return super(Emulator, self).add_instance_from_source(name, path, interfaces,
                                                              image_name, docker_command,
                                                              **docker_build_args)

    @vnv_not_called
    def add_link(self, src_vnf, src_if, dst_vnf, dst_if, sniff=False, **kwargs):
        result = super(Emulator, self).add_link(src_vnf, src_if, dst_vnf, dst_if, sniff, **kwargs)

        if result:
            return result

        params = {
            'source': '{}:{}'.format(src_vnf, src_if),
            'destination': '{}:{}'.format(dst_vnf, dst_if),
            'weight': kwargs.get('weight'),
            'match': kwargs.get('match'),
            'bidirectional': kwargs.get('bidirectional', True),
            'cookie': kwargs.get('cookie'),
            'priority': kwargs.get('priority'),
            'endpoint': self.endpoint
        }

        return EmuNetworkClient().add(params)


class EmulatorInstance(DockerBasedInstance):
    """
    A representation of an instance on the Emulator.
    Should not be created manually but by the Emulator class.
    """

    @property
    def container_name(self):
        return 'mn.{}'.format(self.name)

    def stop(self):
        pass
