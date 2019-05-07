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
