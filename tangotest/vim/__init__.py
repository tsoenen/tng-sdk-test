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

import os


def vim_from_env():
    platform = os.environ.get('TANGOTEST_PLATFORM', 'EMULATOR')
    if platform == 'EMULATOR':
        vnv_checker = bool(os.environ.get('TANGOTEST_VNV_CHECKER', 0))
        enable_learning = bool(os.environ.get('TANGOTEST_ENABLE_LEARNING', 0))
        from tangotest.vim.emulator import Emulator
        vim = Emulator(enable_learning=enable_learning, vnv_checker=vnv_checker)
    elif platform == 'VNV':
        from tangotest.vim.vnv import Vnv
        vim = Vnv()
    else:
        raise Exception('Unkown platform {}'.format(platform))
    return vim
