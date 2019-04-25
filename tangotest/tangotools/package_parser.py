import zipfile
import yaml
from collections import OrderedDict


def parse_package(package_path, package_format='tango'):
    if package_format == 'tango':
        return parse_tango_package(package_path)
    else:
        raise Exception('Specified unsupported package_format {}. Supported formats: tango.'.format(package_format))

def parse_tango_package(package_path)
    # TODO: parametrize function type (virtual, cloud)

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
            if record['content-type'] == 'application/vnd.5gtango.vnfd':
                with z.open(record['source']) as nfd_file:
                    nfd = yaml.safe_load(nfd_file)
                    nfds[nfd['name']] = nfd

    external_ns_cps = [cp['id'] for cp in nsd['connection_points'] if cp['type'] == 'external']
    ns_virtual_links = [vl['connection_points_reference'] for vl in nsd['virtual_links']]
    external_ns_virtual_links = [vl for vl in ns_virtual_links if set(vl) & set(external_ns_cps)]
    external_nfs_cps = list(set(sum(external_ns_virtual_links, [])).difference(external_ns_cps))

    for nf in nsd['network_functions']:
        nf_name = nf['vnf_name']
        nf_id = nf['vnf_id']
        nfd = nfds[nf_name]
        external_nf_cps = [cp.split(':')[1] for cp in external_nfs_cps if cp.split(':')[0] == nf_id]
        nf_virtual_links = [vl['connection_points_reference'] for vl in nfd['virtual_links']]        
        external_nf_virtual_links = [vl for vl in nf_virtual_links if set(vl) & set(external_nf_cps)]
        external_dus_cps = list(set(sum(external_nf_virtual_links, [])).difference(external_nf_cps))
        result[nf_name] = {}
        for du in nfd['virtual_deployment_units']:
            du_name = du['id']
            external_du_cps = [cp.split(':')[1] for cp in external_dus_cps if cp.split(':')[0] == du_name]
            result[nf_name][du_name] = external_du_cps
            
    return result

