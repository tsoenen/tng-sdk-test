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

from functools import wraps


class VnvError(Exception):
    """Raised by the Emulator class when vnv_checker is set and test failed"""
    pass


vnv_checker_data = {}


def vnv_checker_start(f):
    @wraps(f)
    def wrapper(self, *args, **kwargs):
        if self.vnv_checker:
            self._vnv_checker_data = vnv_checker_data.copy()
        return f(self, *args, **kwargs)
    return wrapper


def vnv_checker_stop(f):
    @wraps(f)
    def wrapper(self, *args, **kwargs):
        if self.vnv_checker:
            for k, v in self._vnv_checker_data.items():
                if not v:
                    raise VnvError('Requirement not met: {}'.format(k))
        return f(self, *args, **kwargs)
    return wrapper


def vnv_not_called(f):
    @wraps(f)
    def wrapper(self, *args, **kwargs):
        if self.vnv_checker:
            raise VnvError('Function {} can not be used on the V&V'.format(f.__name__))
        return f(self, *args, **kwargs)
    return wrapper


def vnv_called_once(f):
    @wraps(f)
    def wrapper(self, *args, **kwargs):
        if self.vnv_checker:
            if self._vnv_checker_data['Called {}'.format(f.__name__)]:
                raise VnvError('Function {} can be called only once on the V&V'.format(f.__name__))
            self._vnv_checker_data['Called {}'.format(f.__name__)] = True
        return f(self, *args, **kwargs)
    vnv_checker_data['Called {}'.format(f.__name__)] = False
    return wrapper


def vnv_called_without_parameter(parameter):
    @wraps(f)
    def decorator(f):
        def wrapper(self, *args, **kwargs):
            if self.vnv_checker:
                if kwargs.get(parameter) is not None:
                    raise VnvError('Function {} can not be used with parameter {} on the V&V'.format(f.__name__, parameter))
            return f(self, *args, **kwargs)
        return wrapper
    return decorator
