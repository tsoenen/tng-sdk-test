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
