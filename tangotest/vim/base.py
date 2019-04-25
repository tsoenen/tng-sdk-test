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
    """
    This is a base class for interaction with a virtual infrastructure manager.
    It can not be used directly and must be subclassed for each platform.
    """
    __metaclass__ = ABCMeta

    @abstractproperty
    def InstanceClass(self):
        pass

    @abstractmethod
    def __init__(self):
        """
        This method must be called by subclasses to perform library-specific initialization and
        augmented with a platform-specific initialization.
        """
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
        """
        Run the VIM or connect to the running VIM.
        """
        pass

    @abstractmethod
    def stop(self):
        """
        Stop the VIM or disconnect from it.
        """
        pass

    @abstractmethod
    def _image_exists(self, image):
        """
        Check whether specified image is available on the VIM.

        Args:
            image (str): The name of the image
        """
        pass

    def _add_instance(self, name, interfaces):
        instance = self.InstanceClass(self, name, interfaces)
        self.instances[name] = instance
        return instance

    @abstractmethod
    def add_instances_from_package(self, package, package_format=None):
        """
        Run VNFs using a package.
        The library will run all the VNFs from the package and connect the according to the descriptors.

        Args:
            package (str): The path to the package
            package_format (str): "tango" or "sonata"

        Returns:
            list: The list of (BaseInstance)s
        """
        pass

    @abstractmethod
    def add_instance_from_image(self, name, image, interfaces=None, **args):
        """
        Run an image.

        Args:
            name (str): The name of an instance
            image (str): The name of an image
            interfaces (int) or (list): Network configuration
            args: Platform-specific parameters

        Returns:
            (BaseInstance): The added instance
        """
        pass

    @abstractmethod
    def add_instance_from_source(self, name, path, interfaces=None, permanent_name=None, **args):
        """
        Build and run an image on the VIM.

        Args:
            name (str): The name of an instance
            path (str): The path to the directory containing Dockerfile
            interfaces (int) or (list): Network configuration
            permanent_name (str): The name of an image. If not (None) the image will not be deleted after test execution
            args: Platform-specific parameters

        Returns:
            (BaseInstance): The added instance
        """
        pass

    def add_test_vnf(self, name, vnf_name):
        """
        Add addtitional test VNFs.

        Args:
            name (str): The name of an instance
            vnf_name (str): The name of the VNF

        Returns:
            (BaseInstance): The added instance
        """
        vnf = vnfs.get(vnf_name)
        if not vnf:
            raise Exception('Test vnf {} not found'.format(vnf_name))

        image = 'tango{}'.format(vnf_name)
        if self._image_exists(image):
            return self.add_instance_from_image(name, image, vnf['interfaces'])
        else:
            return self.add_instance_from_source(name, vnf['source'], vnf['interfaces'], permanent_name=image)

    @abstractmethod
    def add_link(self, src_vnf, src_if, dst_vnf, dst_if, sniff=False, **kwargs):
        """
        Add a link between two instances.

        Args:
            src_vnf (str): The name of a source VNF
            src_if (str): The name of a source interface
            dst_vnf (str): The name of a destination VNF
            dst_if (str): The name of a destination interface
            sniff (bool): Add the sniffer to the link

        Returns:
            (bool): ''True'' if successfull
        """

        if not sniff:
            return False

        sniffer_name = 'sniffer_{}_{}_{}_{}'.format(src_vnf, src_if, dst_vnf, dst_if)
        self.add_test_vnf(sniffer_name, 'sniffer')

        self.add_link(src_vnf, src_if,
                      sniffer_name, self.instances[sniffer_name].interfaces[0],
                      sniff=False, **kwargs)

        self.add_link(sniffer_name, self.instances[sniffer_name].interfaces[1],
                      dst_vnf, dst_if,
                      sniff=False, **kwargs)

        return True

    def get_traffic(self, src_vnf, src_if, dst_vnf, dst_if):
        """
        Get sniffed traffic.

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
    """
    A representation of the abstract instance.
    Must be subclassed for each platform.
    Should not be created manually but by the VIM adapter.
    """

    __metaclass__ = ABCMeta

    @abstractmethod
    def execute(self, cmd, stream=False, **kwargs):
        """
        Execute a command or script on the instance.

        Args:
            cmd (str): The command or path to the script

        Returns:
            (str): Output of the executed command or script
        """
        pass

    def get_ip(self, interface):
        """
        Get an IP address of an interface.

        Args:
            interface (int) or (str): A number or name of the interface

        Returns:
            (str) or (None): The IP address of the interface or None if the interface doesn't exist
                             or if the interface has no IP address
        """

        if isinstance(interface, int):
            interface = self.interfaces[interface]
        if not isinstance(interface, str):
            raise Exception('Instance {} has no interface {}.'.format(self.name, interface))

        cmd = 'ip -4 addr show {} | grep -oP \'(?<=inet\s)\d+(\.\d+){{3}}\''.format(interface)
        code, output = self.execute(cmd)

        ip = output.strip()

        if not ip:
            return None

        return ip

    def get_mac(self, interface):
        """
        Get a MAC address of an interface.

        Args:
            interface (int) or (str): A number or name of the interface

        Returns:
            (str) or (None): The MAC address of the interface or None if the interface doesn't exist
        """

        if isinstance(interface, int):
            interface = self.interfaces[interface]
        if not isinstance(interface, str):
            raise Exception('Instance {} has no interface {}.'.format(self.name, interface))

        cmd = 'cat /sys/class/net/{}/address'.foramt(interface)
        code, output = self.execute(cmd)

        mac = output.strip()

        if not mac:
            return None

        return mac

    def get_file(self, path):
        """
        Get file content.

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
        Get records from systemd journal.

        Args:
            params (str): Parameters of the request

        Returns:
            (list): The list of records
        """
        pass

class BaseImmutableInstance(BaseInstance):
    """
    A representation of the abstract instance without direct access
    Must be subclassed for each platform.
    Should not be created manually but by the VIM adapter.
    """

    __metaclass__ = ABCMeta

    def execute(self, *args, **kwargs):
        raise Exception('Executing commands on immutable instances is not supported.')

    @abstractmethod
    def get_ip(self, interface):
        """
        Get an IP address of an interface.

        Args:
            interface (int) or (str): A number or name of the interface

        Returns:
            (str) or (None): The IP address of the interface or None if the interface doesn't exist
                             or if the interface has no IP address
        """
        pass

    @abstractmethod
    def get_mac(self, interface):
        """
        Get a MAC address of an interface.

        Args:
            interface (int) or (str): A number or name of the interface

        Returns:
            (str) or (None): The MAC address of the interface or None if the interface doesn't exist
        """
        pass
