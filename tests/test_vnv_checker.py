import pytest
import time
import inspect, os
from contextlib import contextmanager

from tangotest.vim.emulator import Emulator
from tangotest.tangotools.vnv_checker import VnvError


packages = [{
    'package': '/packages/eu.5gtango.emulator-example-service.0.1.tgo',
    'format': 'tango',
}, {
    'package': '/packages/eu.sonata.emulator-example-service.0.1.son',
    'format': 'sonata',
}]


test_dir = os.path.dirname(os.path.abspath(inspect.getfile(inspect.currentframe())))


@contextmanager
def emulator_with_vnv_checker_and_package():
    vim = Emulator(vnv_checker=True)
    vim.start()
    path = test_dir + packages[0]['package']
    package_format = packages[0]['format']
    vim.add_instances_from_package(package=path, package_format=package_format)
    yield vim
    vim.stop()



@contextmanager
def does_not_raise():
    yield


@pytest.mark.parametrize('calls,expectation', [
    (0, pytest.raises(VnvError)),
    (1, does_not_raise()),
    (2, pytest.raises(VnvError)),
])
def test_vnv_checker_add_instances_from_package_called_once(calls, expectation):
    with expectation:
        with Emulator(vnv_checker=True) as vim:
            for i in range(calls):
                path = test_dir + packages[i]['package']
                package_format = packages[i]['format']
                vim.add_instances_from_package(package=path, package_format=package_format)


@pytest.mark.parametrize('interfaces,expectation', [
    (None, does_not_raise()),
    (2, pytest.raises(VnvError)),
])
def test_vnv_checker_add_instance_from_image_without_interfaces(interfaces, expectation):
    name = 'tangotest_test'
    image = 'ubuntu:trusty'
    with expectation:
        with emulator_with_vnv_checker_and_package() as vim:
            vim.add_instance_from_image(name=name, image=image, interfaces=interfaces)


@pytest.mark.parametrize('interfaces,expectation', [
    (None, does_not_raise()),
    (2, pytest.raises(VnvError)),
])
def test_vnv_checker_add_instance_from_source_without_interfaces(interfaces, expectation):
    name = 'tangotest_test'
    path = test_dir + '/vnfs/empty'
    with expectation:
        with emulator_with_vnv_checker_and_package() as vim:
            vim.add_instance_from_source(name=name, path=path, interfaces=interfaces)


@pytest.mark.parametrize('called,expectation', [
    (False, does_not_raise()),
    (True, pytest.raises(VnvError)),
])
def test_vnv_checker_add_link_not_called(called, expectation):
    with expectation:
        with emulator_with_vnv_checker_and_package() as vim:
            name1 = 'tangotest_test1'
            name2 = 'tangotest_test2'
            image = 'ubuntu:trusty'
            instance1 = vim.add_instance_from_image(name=name1, image=image)
            instance2 = vim.add_instance_from_image(name=name2, image=image)
            if called:
                vim.add_link(name1, 'cp0', name2, 'cp0')
