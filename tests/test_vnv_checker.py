import pytest
import time
import inspect, os

from tangotest.vnv_checker import VnvError


def test_vnv_checker_add_instances_from_package_called_once(emulator_with_vnv_checker_enabled):
    vim = emulator_with_vnv_checker_enabled

    package1 = '/packages/eu.5gtango.emulator-example-service.0.1.tgo'
    package1_format = 'tango'
    package2 = '/packages/eu.sonata.emulator-example-service.0.1.son'
    package2_format = 'sonata'

    test_dir = os.path.dirname(os.path.abspath(inspect.getfile(inspect.currentframe())))
    path1 = test_dir + package1
    path2 = test_dir + package2

    vim.add_instances_from_package(package=path1, package_format=package1_format)

    with pytest.raises(VnvError):
        vim.add_instances_from_package(package=path2, package_format=package2_format)


def test_vnv_checker_add_instance_from_image_without_interfaces(emulator_with_vnv_checker_enabled):
    vim = emulator_with_vnv_checker_enabled
    name1 = 'tangotest_test1'
    name2 = 'tangotest_test2'
    image = 'ubuntu:trusty'
    vim.add_instance_from_image(name=name1, image=image)
    with pytest.raises(VnvError):
        vim.add_instance_from_image(name=name1, image=image, interfaces=2)


def test_vnv_checker_add_instance_from_source_without_interfaces(emulator_with_vnv_checker_enabled):
    vim = emulator_with_vnv_checker_enabled
    name1 = 'tangotest_test1'
    name2 = 'tangotest_test2'
    test_dir = os.path.dirname(os.path.abspath(inspect.getfile(inspect.currentframe())))
    path = test_dir + '/vnfs/empty'
    vim.add_instance_from_source(name=name1, path=path)
    with pytest.raises(VnvError):
        vim.add_instance_from_source(name=name2, path=path, interfaces=2)


def test_vnv_checker_add_link_not_called(emulator_with_vnv_checker_enabled):
    vim = emulator_with_vnv_checker_enabled
    name1 = 'tangotest_test1'
    name2 = 'tangotest_test2'
    image = 'ubuntu:trusty'

    instance1 = vim.add_instance_from_image(name=name1, image=image)
    instance2 = vim.add_instance_from_image(name=name2, image=image)

    with pytest.raises(VnvError):
        vim.add_link(name1, 'cp0', name2, 'cp0')
