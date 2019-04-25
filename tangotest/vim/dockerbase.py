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
from abc import ABCMeta, abstractmethod, abstractproperty
import docker
import requests


from tangotest.vim.base import BaseVIM, BaseInstance


class DockerBasedVIM(BaseVIM):
    __metaclass__ = ABCMeta

    def __init__(self, *args, **kwargs):
        super(DockerBasedVIM, self).__init__(*args, **kwargs)
        self.built_images = []

    @abstractproperty
    def InstanceClass(self):
        return DockerBasedInstance

    def start(self):
        super(DockerBasedVIM, self).start()
        self.docker_client = docker.from_env()

    def stop(self):
        for image in self.built_images:
            self.docker_client.images.remove(image=image)
        super(DockerBasedVIM, self).stop()

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

    def add_instance_from_image(self, name, image, interfaces=None, docker_command=None, **docker_run_args):
        """
        Run a Docker image on the Emulator.

        Args:
            name (str): The name of an instance
            image (str): The name of an image
            interfaces (int) or (list): Network configuration
            docker_command (str): The command to execute when starting the instance

        Returns:
            (EmulatorInstance): The added instance
        """

        if not self._image_exists(image):
            raise Exception('Docker image {} not found'.format(image))

        self.container = self.docker_client.containers.get(name=name, image=image, command=docker_command, **docker_run_args)
        interfaces = ['eth0']

        return self._add_instance(name, interfaces)

    def add_instance_from_source(self, name, path, interfaces=None, permanent_name=None,
                                 docker_command=None, **docker_build_args):
        """
        Build and run a Docker image on the Emulator.

        Args:
            name (str): The name of an instance
            path (str): The path to the directory containing Dockerfile
            interfaces (int) or (list): Network configuration
            permanent_name (str): The name of an image. If not (None) the image will not be deleted after test execution
            docker_command (str): The command to execute when starting the instance
            **docker_build_args: Extra arguments to be used by the Docker engine to build the image

        Returns:
            (EmulatorInstance): The added instance
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


class DockerBasedInstance(BaseInstance):
    """
    A representation of a docker-based instance.
    Should not be created manually but by the DockerBaseVIM class.
    """
    __metaclass__ = ABCMeta

    def __init__(self, vim, name, interfaces=None):
        """
        Initialize the instance.

        Args:
            name (str): The name of an instance
            path (str): The path to the directory containing Dockerfile
            interfaces (list): Network configuration
        """
        self.vim = vim
        self._name = name
        self.docker_client = self.vim.docker_client
        self.interfaces = interfaces or []
        self.output = None
        self.container = self.docker_client.containers.get(self.name)

    @property
    def name(self):
        return self._name

    def execute(self, cmd, stream=False, **kwargs):
        return self.container.exec_run(cmd=['sh', '-c', cmd], stream=stream, **kwargs)
