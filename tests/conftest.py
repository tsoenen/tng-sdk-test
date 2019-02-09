import pytest

from tangotest.vim.emulator import Emulator


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
