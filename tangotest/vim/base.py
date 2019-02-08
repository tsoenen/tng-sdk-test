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

from abc import ABCMeta, abstractmethod, abstractproperty
import json

from tangotest.vnfs import vnfs

class BaseVIM(object):
    __metaclass__ = ABCMeta

    @abstractproperty
    def InstanceClass(self):
        pass

    def __init__(self):
        self.instances = {}

    def __getattr__(self, name):
        if name in self.instances:
            return self.instances[name]
        else:
            raise NameError('name \'{}\' is not defined'.format(name))

    def __enter__(self):
        self.start()
        return self

    def __exit__(self, *args):
        self.stop()

    @abstractmethod
    def start(self):
        pass

    @abstractmethod
    def stop(self):
        pass

    @abstractmethod
    def _image_exists(self, image):
        pass

    def _add_instance(self, name, interfaces):
        instance = self.InstanceClass(self, name, interfaces)
        self.instances[name] = instance
        return instance

    @abstractmethod
    def add_instances_from_package(self, package, package_format=None):
        """
        Run VNFs using package

        Args:
            package (str): Path to the descriptor
            package_format (str): "tango" or "sonata"

        Returns:
            list: The list of (BaseInstance)s
        """
        pass

    @abstractmethod
    def add_instances_from_descriptor(self, descriptor):
        """
        Run a VNF using its descriptor

        Args:
            vnfd (str): Path to the descriptor

        Returns:
            list: The list of (BaseInstance)s
        """
        pass

    @abstractmethod
    def add_instance_from_source(self, name, path, interfaces=None, permanent_name=None, **args):
        """
        Build and run an image on the VIM

        Args:
            name (str): The name of an instance
            path (str): Path to the directory containing Dockerfile
            interfaces (int) or (list): Network configuration

        Returns:
            (BaseInstance): The instance
        """
        pass

    def add_test_vnf(self, name, vnf_name):
        vnf = vnfs.get(vnf_name)
        if not vnf:
            raise Exception('Test vnf {} not found'.format(vnf_name))

        image = 'tango{}'.format(vnf_name)
        if self._image_exists(image):
            self.add_instance_from_image(name, image, vnf['interfaces'])
        else:
            self.add_instance_from_source(name, vnf['source'], vnf['interfaces'], permanent_name=image)

    @abstractmethod
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

        if sniff:
            sniffer_name = 'sniffer_{}_{}_{}_{}'.format(src_vnf, src_if, dst_vnf, dst_if)
            self.add_test_vnf(sniffer_name, 'sniffer')

            self.add_link(src_vnf, src_if,
                          sniffer_name, self.instances[sniffer_name].interfaces[0],
                          sniff=False, **kwargs)

            self.add_link(sniffer_name, self.instances[sniffer_name].interfaces[1],
                          dst_vnf, dst_if,
                          sniff=False, **kwargs)

            return True
        else:
            return False

    def get_traffic(self, src_vnf, src_if, dst_vnf, dst_if):
        """
        Get sniffed traffic

        Args:
            src_vnf (str): The name of a source VNF
            src_if (str): The name of an interface of a source VNF
            dst_vnf (str): The name of a destination VNF
            dst_if (str): The name of an interface of a destination VNF

        Returns:
            (generator): Sniffed packets
        """

        sniffer_name = 'sniffer_{}_{}_{}_{}'.format(src_vnf, src_if, dst_vnf, dst_if)
        sniffer_file = 'tangosniffed.json'
        sniffer = self.instances.get(sniffer_name)

        if not sniffer:
            raise Exception('Sniffer is not added to this link')

        traffic = sniffer.get_file(sniffer_file)
        if not traffic:
            return []

        traffic += ']'
        traffic = json.loads(traffic)
        traffic = [packet['_source']['layers'] for packet in traffic]
        return traffic


class BaseInstance(object):
    """A representation of an Emulator instance"""

    __metaclass__ = ABCMeta

    @abstractmethod
    def execute(self, cmd, stream=False, **kwargs):
        """
        Execute a command or script on the instance

        Args:
            cmd (str): The command or path to the script

        Returns:
            (str): stdout and stderr
        """
        pass

    def get_ip(self, interface):
        """
        Get IP address of an interface

        Args:
            interface (int) or (str): Number or name of the interface

        Returns:
            (str) or (None): IP address of an interface or None if an interface has no IP address
        """

        if isinstance(interface, int):
            interface = self.interfaces[interface]
        if isinstance(interface, str):
            cmd = 'ip -4 addr show {} | grep -oP \'(?<=inet\s)\d+(\.\d+){{3}}\''.format(interface)
            code, output = self.execute(cmd)

            ip = output.strip()

            if not ip:
                raise Exception('Instance {} has no interface {}.'.format(self.name, interface))
            else:
                return ip

    def get_file(self, path):
        """
        Get file content

        Args:
            path (str): A path to the file

        Returns:
            (str): The content of the file
        """
        cmd = 'cat {}'.format(path)
        code, output = self.execute(cmd=cmd)
        if code != 0:
            raise IOError('No such file or directory: \'{}\''.format(path))
        return output

    def get_journal(self, params):
        """
        Get records from systemd journal

        Args:
            params (str): Parameters of the request

        Returns:
            (list): List of records
        """
        pass
