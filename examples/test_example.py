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

import pytest
import datetime
import time

from tangotest.vim.emulator import Emulator
from tangotest.utils import SNORT_TIME_FORMAT, SNIFFER_TIME_FORMAT


@pytest.fixture(scope='module')
def testbed():
    with Emulator() as vim:
        vim.add_instance_from_source('client', 'client')
        vim.add_instance_from_source('server', 'server')
        vim.add_instance_from_source('firewall', 'firewall', ['input', 'output'])
        vim.add_instance_from_source('snort', 'snort', ['input', 'output'])
        vim.add_link('client', 'emu0', 'firewall', 'input')
        vim.add_link('firewall', 'output', 'snort', 'input', sniff=True)
        vim.add_link('snort', 'output', 'server', 'emu0')
        yield vim


@pytest.mark.parametrize('test_input,expected_output', [
    ('/', 'Home Page'),
    ('/about', 'Test Server'),
    ('/error', 'Error 404')
])
def test_server(test_input, expected_output, testbed):
    test_command = 'curl -s {}{}'.format(testbed.server.get_internal_ip('emu0'), test_input)
    _, actual_output = testbed.client.execute(test_command)

    assert expected_output == actual_output


@pytest.mark.parametrize('test_input,expected_output', [
    ('/about', []),
    ('/restricted/', ['Requested restricted content'])
])
def test_snort(test_input, expected_output, testbed):
    start_time = datetime.datetime.utcnow()

    server_ip = testbed.server.get_internal_ip('emu0')
    test_command = 'curl -s {}{}'.format(server_ip, test_input)
    testbed.client.execute(test_command)
    time.sleep(1)

    alert_records = testbed.snort.get_file('/snort-logs/alert')
    actual_output = []
    for record in alert_records.splitlines():
        record_time = '{}/{}'.format(start_time.year, record.split()[0])
        record_time = datetime.datetime.strptime(record_time, SNORT_TIME_FORMAT)
        if record_time >= start_time:
            actual_output.append(record)

    if len(expected_output) != len(actual_output):
        raise AssertionError('Lengths are not equal')

    for i in range(len(expected_output)):
        if expected_output[i] not in actual_output[i]:
            raise AssertionError(expected_output[i])


def test_firewall(testbed):
    test_command = 'iptables -P FORWARD DROP'
    testbed.firewall.execute(test_command)

    server_ip = testbed.server.get_internal_ip('emu0')
    client_ip = testbed.client.get_internal_ip('emu0')
    test_command = 'ping -c 1 -W 5 {}'.format(server_ip)

    start_time = datetime.datetime.utcnow()
    testbed.client.execute(test_command)

    packets = testbed.get_traffic('firewall', 'output', 'snort', 'input')

    for packet in packets:
        frame_time = packet['frame']['frame.time']
        frame_date, frame_nanoseconds = frame_time.split('.')
        frame_time = '.'.join([frame_date, frame_nanoseconds[:6]])
        frame_time = datetime.datetime.strptime(frame_time, SNIFFER_TIME_FORMAT)
        if frame_time > start_time:
            if 'ip' in packet:
                assert client_ip != packet['ip']['ip.src']
