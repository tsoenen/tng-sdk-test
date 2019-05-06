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

import zipfile
import yaml


def parse_package(package_path, package_format='tango'):
    """
    Extract information needed for testing.

    Output example:
        {
            'ns_name': 'my_ns',
            'testing_tags': ['tag1', 'tag2'],
            'endpoints': {
                'nf1': {
                    'vdu1': ['input', 'output']
                }
            }
        }
    """
    # TODO: parametrize functions type (virtual, cloud)
    # TODO: parametrize platform type (5gtango, osm, onap)
    # TODO: support multiple NSDs

    if package_format == 'tango':
        return parse_tango_package(package_path)
    else:
        raise Exception('Specified unsupported package_format {}. Supported formats: tango.'.format(package_format))


def parse_tango_package(package_path):
    def extract_external_cps(descriptor, upper_level_cps):
        virtual_links = [vl['connection_points_reference'] for vl in descriptor['virtual_links']]
        external_virtual_links = [vl for vl in virtual_links if set(vl) & set(upper_level_cps)]
        external_cps = list(set(sum(external_virtual_links, [])).difference(upper_level_cps))
        return external_cps

    result = {}
    nsd = None
    nfds = {}

    with zipfile.ZipFile(package_path, "r") as z:
        with z.open('TOSCA-Metadata/NAPD.yaml') as pd_file:
            pd = yaml.safe_load(pd_file)

        for record in pd['package_content']:
            if record['content-type'] == 'application/vnd.5gtango.nsd':
                if nsd:
                    raise Exception('Only one NSD can be in the package')
                with z.open(record['source']) as nsd_file:
                    nsd = yaml.safe_load(nsd_file)
                result['tags'] = record.get('tags', [])
                result['testing_tags'] = record.get('testing_tags', [])
            if record['content-type'] == 'application/vnd.5gtango.vnfd':
                with z.open(record['source']) as nfd_file:
                    nfd = yaml.safe_load(nfd_file)
                    nfds[nfd['name']] = nfd

    result['ns_name'] = nsd['name']
    result['ns_version'] = nsd['version']
    result['ns_vendor'] = nsd['vendor']
    result['endpoints'] = {}

    external_ns_cps = [cp['id'] for cp in nsd['connection_points'] if cp['type'] == 'external']
    external_nfs_cps = extract_external_cps(nsd, external_ns_cps)

    for nf in nsd['network_functions']:
        nf_name = nf['vnf_name']
        nf_id = nf['vnf_id']
        nfd = nfds[nf_name]
        external_nf_cps = [cp.split(':')[1] for cp in external_nfs_cps if cp.split(':')[0] == nf_id]
        external_dus_cps = extract_external_cps(nfd, external_nf_cps)

        result['endpoints'][nf_name] = {}
        for du in nfd['virtual_deployment_units']:
            du_name = du['id']
            external_du_cps = [cp.split(':')[1] for cp in external_dus_cps if cp.split(':')[0] == du_name]
            result['endpoints'][nf_name][du_name] = external_du_cps

    return result
