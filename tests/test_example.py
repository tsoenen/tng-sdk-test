import pytest
import datetime
import time

from tangotest.vim.emulator import Emulator


SKIP = True


@pytest.fixture(scope='function')
def vim():
    with Emulator() as vim:
        yield vim


@pytest.fixture(scope='function')
def vnf(vim):
    name = 'tangotest_test'
    image = 'ubuntu:trusty'
    instance = vim.add_instance_from_image(name=name, image=image)
    return instance


@pytest.mark.skip(reason="TODO")
def test_add_instance_from_package(vim):
    pass


@pytest.mark.skip(reason="TODO")
def test_add_instance_from_vnfd(vim):
    pass


@pytest.mark.parametrize('interfaces,expected_interfaces', [
    (None, ['cp0']),
    (3, ['cp0', 'cp1', 'cp2']),
    (['input', 'output', 'management'], ['input', 'output', 'management']),
])
@pytest.mark.skipif(SKIP)
def test_add_instance_from_image(vim, interfaces, expected_interfaces):
    name = 'tangotest_test'
    image = 'ubuntu:trusty'
    instance = vim.add_instance_from_image(name=name, image=image, interfaces=interfaces)
    for interface in expected_interfaces:
        cmd = 'cat /sys/class/net/{}/operstate'.format(interface)
        exec_code, exec_output = instance.execute(cmd)
        assert exec_code == 0
        assert exec_output.strip() == 'up'


@pytest.mark.skipif(SKIP)
def test_add_instance_from_source(vim):
    name = 'tangotest_test'
    path = './vnfs/empty'
    interface = 'cp0'
    instance = vim.add_instance_from_image(name=name, path=path, interfaces=interfaces)
    cmd = 'cat /sys/class/net/{}/operstate'.format(interface)
    exec_code, exec_output = instance.execute(cmd)
    assert exec_code == 0
    assert exec_output.strip() == 'up'


@pytest.mark.parametrize('add_link,expected_exec_code', [
    (False, 1),
    (True, 0),
])
@pytest.mark.skipif(SKIP)
def test_add_link(vim, add_link, expected_exec_code):
    image = 'ubuntu:trusty'

    name1 = 'tangotest_test1'
    instance1 = vim.add_instance_from_image(name=name1, image=image)
    instance1_ip = instance1.get_ip(0)

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


@pytest.mark.skip(reason="TODO")
def test_get_traffic(vim):
    pass


# Instance

@pytest.mark.parametrize('cmd,expected_exec_output,expected_exec_code', [
    ('true', '', 0),
    ('false', '', 1),
    ('echo hello', 'hello', 0),
])
def test_execute(vnf, cmd, expected_exec_output, expected_exec_code):
    exec_code, exec_output = vnf.execute(cmd)
    assert exec_code == expected_exec_code
    assert exec_output.strip() == expected_exec_output.strip()


def test_get_ip(vnf):
    ip = vnf.get_ip(0)
    cmd = 'ping -c1 -W1 {}'.format(ip)
    exec_code, exec_output = vnf.execute(cmd)
    assert exec_code == 0


def test_get_file(vnf):
    cmd = 'echo "hello\nworld" > test.txt'
    vnf.execute(cmd)
    assert 'hello\nworld' == vnf.get_file('test.txt').strip()
    


@pytest.mark.skip(reason="TODO")
def test_get_journal(vnf):
    pass
