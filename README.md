[![Join the chat at https://gitter.im/sonata-nfv/Lobby](https://badges.gitter.im/Join%20Chat.svg)](https://gitter.im/sonata-nfv/Lobby)
[![Documentation Status](https://readthedocs.org/projects/tng-sdk-test/badge/?version=latest)](https://tng-sdk-test.readthedocs.io/en/latest/?badge=latest)
[![Build Status](https://jenkins.sonata-nfv.eu/buildStatus/icon?job=tng-sdk-test-pipeline/master)](https://jenkins.sonata-nfv.eu/job/tng-sdk-test-pipeline/job/master/)

<p align="center"><img src="https://github.com/sonata-nfv/tng-api-gtw/wiki/images/sonata-5gtango-logo-500px.png" /></p>

# tng-sdk-test

This repository contains a Python library `tangotest` for automated functional testing of VNFs.

[The Emulator](https://osm.etsi.org/wikipub/index.php/VIM_emulator) is a light-weight emulation platform based on Containernet. Containernet is Mininet fork adding support for container-based (e.g. Docker) emulated hosts.
VIM-EMU is used by the library to run tests locally.
Then the library can be used to build a probe and generate a test descriptor to run tests on the V&V platform.

## Requirements

- Ubuntu 16.04+
- python 2.7

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

In order to run tests locally, the Emulator needs to be installed separately.
[Installation instructions for the Emulator](https://osm.etsi.org/wikipub/index.php/VIM_emulator).

## Usage

[Documentation](https://tng-sdk-test.readthedocs.io/en/latest/index.html)


### Examples
See [examples](https://github.com/sonata-nfv/tng-sdk-test/tree/master/examples) folder of this repository


## License

This 5GTANGO component is published under Apache 2.0 license. Please see the LICENSE file for more details.

---
#### Lead Developers

The following lead developers are responsible for this repository and have admin rights. They can, for example, merge pull requests.

- Askhat Nuriddinov ([@askmyhat](https://github.com/askmyhat))

#### Feedback-Channel

* Please use the GitHub issues to report bugs.

