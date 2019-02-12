import pytest
import time


@pytest.mark.parametrize('package,package_format,expected_instances', [
    ('./packages/eu.5gtango.emulator-example-service.0.1.tgo', 'tango', ['vnf0.vdu01', 'vnf1.vdu01']),
    ('./packages/eu.sonata.emulator-example-service.0.1.son', 'sonata', ['empty_vnf1', 'empty_vnf2', 'empty_vnf3']),
])
def test_add_instances_from_package(vim, package, package_format, expected_instances):
    expected_interfaces = ['input', 'output', 'mgmt']
    actual_instances = vim.add_instances_from_package(package=package, package_format=package_format)

    assert len(actual_instances) == len(expected_instances)

    actual_instances.sort(key=lambda x: x.name)

    for i in range(len(expected_instances)):
        actual_instance = actual_instances[i]
        expected_instance = expected_instances[i]
        assert actual_instance.name == expected_instance

        for interface in expected_interfaces:
            cmd = 'cat /sys/class/net/{}/operstate'.format(interface)
            exec_code, exec_output = actual_instance.execute(cmd)
            assert exec_code == 0
            assert exec_output.strip() == 'up'


@pytest.mark.skip(reason="TODO")
def test_add_instance_from_vnfd(vim):
    pass


@pytest.mark.parametrize('interfaces,expected_interfaces', [
    (None, ['cp0']),
    (3, ['cp0', 'cp1', 'cp2']),
    (['input', 'output', 'management'], ['input', 'output', 'management']),
])
def test_add_instance_from_image(vim, interfaces, expected_interfaces):
    name = 'tangotest_test'
    image = 'ubuntu:trusty'
    instance = vim.add_instance_from_image(name=name, image=image, interfaces=interfaces)
    for interface in expected_interfaces:
        cmd = 'cat /sys/class/net/{}/operstate'.format(interface)
        exec_code, exec_output = instance.execute(cmd)
        assert exec_code == 0
        assert exec_output.strip() == 'up'


def test_add_instance_from_source(vim):
    name = 'tangotest_test'
    path = './vnfs/empty'
    interface = 'cp0'
    instance = vim.add_instance_from_source(name=name, path=path)
    cmd = 'cat /sys/class/net/{}/operstate'.format(interface)
    exec_code, exec_output = instance.execute(cmd)
    assert exec_code == 0
    assert exec_output.strip() == 'up'


@pytest.mark.parametrize('add_link,expected_exec_code', [
    (False, 1),
    (True, 0),
])
def test_add_link(vim, add_link, expected_exec_code):
    image = 'ubuntu:trusty'

    name1 = 'tangotest_test1'
    instance1 = vim.add_instance_from_image(name=name1, image=image)

    name2 = 'tangotest_test2'
    instance2 = vim.add_instance_from_image(name=name2, image=image)
    instance2_ip = instance2.get_ip(0)

    if add_link:
        vim.add_link(name1, 'cp0', name2, 'cp0')

    cmd = 'ping -c1 -W1 {}'.format(instance2_ip)
    exec_code, exec_output = instance1.execute(cmd)
    assert exec_code == expected_exec_code


@pytest.mark.parametrize('test_vnf', [
    'sniffer', 'generator'
])
@pytest.mark.skip(reason="TODO")
def test_add_test_vnf(vim, test_vnf):
    pass


def test_get_traffic(vim):
    image = 'ubuntu:trusty'

    name1 = 'tangotest_test1'
    instance1 = vim.add_instance_from_image(name=name1, image=image)

    name2 = 'tangotest_test2'
    instance2 = vim.add_instance_from_image(name=name2, image=image)
    instance2_ip = instance2.get_ip(0)

    vim.add_link(name1, 'cp0', name2, 'cp0', sniff=True)
    traffic_start = vim.get_traffic(name1, 'cp0', name2, 'cp0')

    cmd = 'ping -c1 -W1 {}'.format(instance2_ip)
    exec_code, exec_output = instance1.execute(cmd)
    assert exec_code == 0

    time.sleep(10)
    traffic_end = vim.get_traffic(name1, 'cp0', name2, 'cp0')

    assert len(traffic_start) < len(traffic_end)
