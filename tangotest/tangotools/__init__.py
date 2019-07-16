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


import yaml
from tangotest.tangotools.package_parser import parse_package
from tangotest.tangotools.probe_builder import build_probe
from tangotest.tangotools.descriptor_generator import generate_test_descriptor


def create_vnv_test(source, package, descriptor, probe=None):
    """
    Prepare test for uploading to the V&V platform.

    Args:
        source (str): The path of the directory with test files.
        package (str): The path of the package.
        descriptor (str): The path of the generated test descriptor.
        probe (str): The name of the generated probe. Default value 'tng-sdk-test-<datetime>''
    """

    probe = build_probe(source, probe)

    package_data = parse_package(package)
    with open(descriptor, 'w') as f:
        yaml.dump(generate_test_descriptor(package_data), f)

    return
