import pytest
import datetime
import time

from tangotest.vim.emulator import Emulator
from tangotest.common import SNORT_TIME_FORMAT


@pytest.fixture(scope='module')
def testbed():
    with Emulator() as emulator:
        client = emulator.add_instance_from_image('client', 'tangoclient')
        server = emulator.add_instance_from_image('server', 'tangoserver')
        snort = emulator.add_instance_from_image('snort', 'tangosnort', interfaces=['input', 'output'])
        emulator.add_link('client', client.interfaces[0], 'snort', 'input')
        emulator.add_link('server', server.interfaces[0], 'snort', 'output')
        yield emulator


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
 
    test_command = 'curl -s {}{}'.format(testbed.server.get_ip(0), test_input)
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

