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


def generate_test_descriptor(ns_name, testing_tags, endpoints):
    return {
        'descriptor_schema': 'https://raw.githubusercontent.com/sonata-nfv/tng-schema/master/test-descriptor/testdescriptor-schema.yml',
        'vendor': 'eu.5gtango',
        'name': 'tng-sdk-test-{}'.format(ns_name),
        'version': '0.1',
        'author': 'tng-sdk-test',
        'description': 'Functional test for {}'.format(ns_name),
        'testing_tags': testing_tags,
        'test_category': 'functional',
        'phases': [{
            'id': 'setup',
            'steps': [{
                'name': 'deployment',
                'description': 'Deploying a NS',
                'action': 'deploy',
            }, {
                'name': 'configuration',
                'description': 'Configuring test',
                'action': 'configure',
                'probes': [{
                    'id': 'tester',
                    'name': 'tester',
                    'image': 'registry.sonata-nfv.eu:5000/tng-sdk-test-{}:latest'.format(ns_name),
                    'description': 'A container with tng-sdk-test and the test code',
                    'parameters': [{
                        '{}_{}'.format(vnf, interface): '$({}/endpoints/name:{}/address)'.format(vnf, interface)
                    } for vnf in endpoints for interface in endpoints[vnf]],
                }],
            }],
        }, {
            'id': 'excercise',
            'steps': [{
                'name': 'run_tests',
                'description': 'Run a probe with tng-sdk-test and the test code',
                'run': 'tester',
                'index': '0',
                'start_delay': '0',
                'instances': '1',
                'output': [{
                    'results': 'logs.txt',
                    'verdict': 'status.txt',
                }],
            }],
        }, {
            'id': 'verification',
            'steps': [{
                'name': 'tester',
                'description': 'Check the exit-code of the test',
                'step': 'configure_service',
                'condition': [{
                    'type': 'json',
                    'name': 'test-exit-code',
                    'file': 'status.txt',
                    'find': 'exit-code',
                    'value': '0',
                    'verdict': 'pass',
                    'condition': '=',
                }]
            }]
        }]
    }
