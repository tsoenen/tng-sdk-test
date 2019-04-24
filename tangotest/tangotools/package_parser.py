import zipfile
import yaml


def parse_package(package_path)
    with zipfile.ZipFile(package_path, "r") as z:
        nsd_path = None
        vnfd_paths = []

        pd_path = 'TOSCA-Metadata/NAPD.yaml'
        with z.open(pd_path) as pd_file:
            pd = yaml.safe_load(pd_file)

        for record in pd['package_content']:
            if record['content-type'] == 'application/vnd.5gtango.nsd':
                if nsd_path:
                    raise Exception('Only one NSD can be in the package')
                nsd_path = record['source']
            if record['content-type'] == 'application/vnd.5gtango.vnfd':
                vnfd_paths.append(record['source'])

        with z.open(nsd_path) as nsd_file:
            nsd = yaml.safe_load(nsd_file)

        for vnfd_path in vnfd_paths:
            with z.open(vnfd_path) as vnfd_file:
                vnfd = yaml.safe_load(vnfd_file)


