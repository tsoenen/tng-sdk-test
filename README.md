[![Join the chat at https://gitter.im/sonata-nfv/Lobby](https://badges.gitter.im/Join%20Chat.svg)](https://gitter.im/sonata-nfv/Lobby)
[![Documentation Status](https://readthedocs.org/projects/tng-sdk-test/badge/?version=latest)](https://tng-sdk-test.readthedocs.io/en/latest/?badge=latest)
[![Build Status](https://jenkins.sonata-nfv.eu/buildStatus/icon?job=tng-sdk-test-pipeline/master)](https://jenkins.sonata-nfv.eu/job/tng-sdk-test-pipeline/job/master/)

<p align="center"><img src="https://github.com/sonata-nfv/tng-api-gtw/wiki/images/sonata-5gtango-logo-500px.png" /></p>

# tng-sdk-test

This repository contains a Python library `tangotest` for automated functional testing of VNFs.

The library helps test developers to write functional tests in Python and run locally or in CI/CD environments.
Using the library, test developers choose which infrastructure to use, which network services and test VNFs to launch, how to interconnect them, how to trigger the test process and inspect, verify and validate the output against the expected values and conditions.
Test developers can use network service packages to deploy services or can compose them directly in a test code.


## Requirements

- Ubuntu 16.04+
- python 2.7

## Dependencies

VIM-EMU is a light-weight emulation platform that is used by the library to run tests locally.
Detailed describtion and installation instructions can be found on the project page:
[https://osm.etsi.org/wikipub/index.php/VIM_emulator](https://osm.etsi.org/wikipub/index.php/VIM_emulator).

## Installation

```
git clone https://github.com/sonata-nfv/tng-sdk-test.git
cd tng-sdk-test
python2 setup.py install
```

or

```
pip2 install git+https://github.com/sonata-nfv/tng-sdk-test
```


## Usage

[Documentation](https://tng-sdk-test.readthedocs.io/en/latest/index.html)


### Examples

A simple example of library usage:

```
from tangotest.vim.emulator import Emulator


with Emulator() as vim:
    client = vim.add_instance_from_source('client', './client_vnf', ['emu0'])
    server = vim.add_instance_from_source('server', './server_vnf', ['emu0'])
    vim.add_link('client', 'emu0', 'server', 'emu0')

    cmd = 'curl {}'.format(server.get_ip('emu0'))
    exec_code, output = client.execute(cmd)

    assert exec_code == 0
    assert output == 'Hello World!'
```

You can use [UnitTest](https://docs.python.org/2/library/unittest.html) or [pytest](https://docs.pytest.org/en/latest/) to manage your test cases.

*Note:* Tests need to be run with `sudo`.

See [examples](https://github.com/sonata-nfv/tng-sdk-test/tree/master/examples) folder of this repository for more examples.

## License

This 5GTANGO component is published under Apache 2.0 license. Please see the LICENSE file for more details.

---
#### Lead Developers

The following lead developers are responsible for this repository and have admin rights. They can, for example, merge pull requests.

- Askhat Nuriddinov ([@askmyhat](https://github.com/askmyhat))

#### Feedback-Channel

* Mailing list [sonata-dev-list](mailto:sonata-dev@lists.atosresearch.eu)
* Gitter room [![Gitter](https://badges.gitter.im/sonata-nfv/Lobby.svg)](https://gitter.im/sonata-nfv/Lobby?utm_source=badge&utm_medium=badge&utm_campaign=pr-badge)
