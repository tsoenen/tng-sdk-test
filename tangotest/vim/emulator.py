import os
import docker
import requests

from mininet.node import RemoteController

from emuvim.cli.rest.compute import RestApiClient as EmuComputeClient
from emuvim.cli.rest.network import RestApiClient as EmuNetworkClient

from emuvim.dcemulator.net import DCNetwork
from emuvim.api.rest.rest_api_endpoint import RestApiEndpoint
from emuvim.api.sonata import SonataDummyGatekeeperEndpoint
from emuvim.api.tango import TangoLLCMEndpoint

from tangotest.vim.base import BaseVIM, BaseInstance
from tangotest.utils import get_free_tcp_port


class Emulator(BaseVIM):
    def __init__(self, *args, **kwargs):
        super(Emulator, self).__init__(*args, **kwargs)
        self.built_images = []

    @property
    def InstanceClass(self):
        return EmulatorInstance

    def start(self):
        super(Emulator, self).start()

        self.docker_client = docker.from_env()

        self.net = DCNetwork(controller=RemoteController, monitor=False, enable_learning=False)
        self.datacenter = self.net.addDatacenter('dc1')

        endpoint_ip = '0.0.0.0'
        endpoint_port = get_free_tcp_port()
        self.endpoint = 'http://{}:{}'.format(endpoint_ip, endpoint_port)

        self.rest_api = RestApiEndpoint(endpoint_ip, endpoint_port)
        self.rest_api.connectDCNetwork(self.net)
        self.rest_api.connectDatacenter(self.datacenter)
        self.rest_api.start()

        sonata_ip = '0.0.0.0'
        sonata_port = get_free_tcp_port()
        self.sonata_address = 'http://{}:{}'.format(sonata_ip, sonata_port)
        self.sonata_gatekeeper = SonataDummyGatekeeperEndpoint(sonata_ip, sonata_port)
        self.sonata_gatekeeper.connectDatacenter(self.datacenter)
        self.sonata_gatekeeper.start()

        tango_ip = '0.0.0.0'
        tango_port = get_free_tcp_port()
        self.tango_address = 'http://{}:{}'.format(tango_ip, tango_port)
        self.tango_gatekeeper = TangoLLCMEndpoint(tango_ip, tango_port)
        self.tango_gatekeeper.connectDatacenter(self.datacenter)
        self.tango_gatekeeper.start()

        self.net.start()

    def stop(self):
        for instance in self.instances.values():
            instance.stop()

        for image in self.built_images:
            self.docker_client.images.remove(image=image)

        self.rest_api.stop()
        self.net.stop()

    def _image_exists(self, image):
        try:
            self.docker_client.images.get(image)
        except docker.errors.ImageNotFound:
            if ':' in image:
                image_name, image_tag = image.split(':')
            else:
                image_name = image
                image_tag = 'latest'
            url = 'https://index.docker.io/v1/repositories/{}/tags/{}'.format(image_name, image_tag)
            if not requests.get(url).ok:
                return False
        except docker.errors.APIError as e:
            raise e
        return True

    def add_instances_from_package(self, package, package_format=None):
        """
        Run VNFs using 5GTANGO package

        Args:
            package (str): Path to a descriptor
            package_format (str): "tango" or "sonata"

        Returns:
            list: The list of (EmulatorInstance)s
        """
        if not os.path.isfile(package):
            raise Exception('Package {} not found'.format(package))

        if not package_format:
            package_format = 'tango'

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
            interfaces = [i['intf_name'] for i in instance.getNetworkStatus()]
            instances.append(self._add_instance(name, interfaces))

        return instances

    def add_instances_from_descriptor(self, descriptor):
        """
        Run a VNF using its descriptor

        Args:
            vnfd (str): Path to a descriptor

        Returns:
            list: The list of (EmulatorInstance)s
        """
        raise Exception('Not implemented yet')

    def add_instance_from_image(self, name, image, interfaces=None, docker_command=None):
        """
        Run a Docker image on the Emulator

        Args:
            name (str): The name of an instance
            image (str): The image to instatiate
            interfaces (int) or (list): Network configuration
            docker_command (str): The command to execute when running the image

        Returns:
            (EmulatorInstance): The instance
        """

        if not self._image_exists(image):
            raise Exception('Docker image {} not found'.format(image))

        if not interfaces:
            interfaces = ['cp0']
        elif isinstance(interfaces, int):
            interfaces = ['cp{}'.format(i) for i in range(interfaces)]
        elif not isinstance(interfaces, list):
            raise Exception('Parameter (interfaces) must be None, integer or string, passed {}'.format(type(interfaces)))

        network = ','.join(['(id={})'.format(i) for i in interfaces])

        params = {
            'name': name,
            'image': image,
            'command': docker_command,
            'network': network,
            'endpoint': self.endpoint,
            'datacenter': 'dc1'
        }

        EmuComputeClient().start(params)

        return self._add_instance(name, interfaces)

    def add_instance_from_source(self, name, path, interfaces=None, permanent_name=None,
                                 docker_command=None, **docker_build_args):
        """
        Build and run a Docker image on the Emulator

        Args:
            name (str): The name of an instance
            path (str): Path to the directory containing Dockerfile
            interfaces (int) or (list): Network configuration
            docker_command (str): The command to execute when running the image

        Returns:
            (EmulatorInstance): The instance
        """

        if path[-1] != '/':
            path += '/'

        if not os.path.isfile('{}Dockerfile'.format(path)):
            raise Exception('Dockerfile in {} not found'.format(path))

        if permanent_name:
            tag = permanent_name
        else:
            tag = 'tangotest{}'.format(name)
        docker_image, _ = self.docker_client.images.build(path=path, **docker_build_args)
        docker_image.tag(tag)

        if not permanent_name:
            self.built_images.append(tag)

        return self.add_instance_from_image(name, tag, interfaces)

    def add_link(self, src_vnf, src_if, dst_vnf, dst_if, sniff=False, **kwargs):
        """
        Add link between two instances

        Args:
            src_vnf (str): The name of a source VNF
            src_if (str): The name of an interface of a source VNF
            dst_vnf (str): The name of a destination VNF
            dst_if (str): The name of an interface of a destination VNF
            sniff (bool): Add sniffer to the link

        Returns:
            (bool): ''True'' if successfull
        """

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


class EmulatorInstance(BaseInstance):
    def __init__(self, vim, name, interfaces):
        self.vim = vim
        self.name = name
        self.docker_client = self.vim.docker_client
        self.container = self.docker_client.containers.get('mn.{}'.format(name))
        self.interfaces = interfaces
        self.output = None

    def execute(self, cmd, stream=False, **kwargs):
        return self.container.exec_run(cmd=['sh', '-c', cmd], stream=stream, **kwargs)

    def stop(self):
        self.container.kill()
        self.container.remove()
