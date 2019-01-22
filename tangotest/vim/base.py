from abc import ABCMeta, abstractmethod, abstractproperty
import json


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

    def _add_instance(self, name, interfaces):
        instance = self.InstanceClass(self, name, interfaces)
        self.instances[name] = instance
        return instance

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

    @abstractmethod
    def add_test_vnf(self, name, vnf_name):
        pass

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
        cmd = 'cat {}'.format(path)
        code, output = self.execute(cmd=cmd)
        if code != 0:
            raise IOError('No such file or directory: \'{}\''.format(path))
        return output

    def get_stdout(self):
        pass

    def get_stderr(self):
        pass

    def get_jounalctl(self, params):
        pass

    @abstractmethod
    def execute(self, cmd, stream=False, **kwargs):
        pass
