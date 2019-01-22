import pytest
import datetime
import time
import json

from tangotest.vim.emulator import Emulator
from tangotest.common import SNORT_TIME_FORMAT


@pytest.fixture(scope='module')
def testbed():
    with Emulator() as vim:
        client = vim.add_instance_from_image('client', 'tangoclient')
        server = vim.add_instance_from_image('server', 'tangoserver')
        firewall = vim.add_instance_from_image('firewall', 'tangofirewall', interfaces=['input', 'output'])
        snort = vim.add_instance_from_image('snort', 'tangosnort', interfaces=['input', 'output'])
        vim.add_link('client', 'cp0', 'firewall', 'input')
        vim.add_link('firewall', 'output', 'snort', 'input', sniff=True)
        vim.add_link('snort', 'output', 'server', 'cp0')
        yield vim 


@pytest.mark.parametrize('test_input,expected_output', [
    ('/', 'Home Page'),
    ('/about', 'Test Server'),
    ('/error', 'Error 404')
])
def test_server(test_input, expected_output, testbed):
    test_command = 'curl -s {}{}'.format(testbed.server.get_ip(0), test_input)
    _, actual_output = testbed.client.execute(test_command)

    assert expected_output == actual_output


@pytest.mark.parametrize('test_input,expected_output', [
    ('/about', []),
    ('/restricted/', ['Requested restricted content'])
])
def test_snort(test_input, expected_output, testbed):
    start_time = datetime.datetime.utcnow()

    server_ip = testbed.server.get_ip(0)
    test_command = 'curl -s {}{}'.format(server_ip, test_input)
    testbed.client.execute(test_command)
    time.sleep(1)

    alert_records = testbed.snort.get_file('/snort-logs/alert')
    actual_output = []
    for record in alert_records.splitlines():
        record_time = datetime.datetime.strptime(str(datetime.datetime.utcnow().year) + '/' + record.split()[0], SNORT_TIME_FORMAT)
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
    
    server_ip = testbed.server.get_ip(0)
    client_ip = testbed.client.get_ip(0)
    test_command = 'ping -c 1 -W 5 {}'.format(server_ip)
    
    start_time = datetime.datetime.utcnow()
    testbed.client.execute(test_command)
    
    packets = testbed.get_traffic('firewall', 'output', 'snort', 'input')
    
    for packet in packets:
        frame_time = packet['frame']['frame.time']
        frame_date, frame_nanoseconds = frame_time.split('.')
        frame_time = '.'.join([frame_date, frame_nanoseconds[:6]])
        frame_time = datetime.datetime.strptime(frame_time, '%b %d, %Y %H:%M:%S.%f')
        if frame_time > start_time:
            if 'ip' in packet:
                assert client_ip != packet['ip']['ip.src']
