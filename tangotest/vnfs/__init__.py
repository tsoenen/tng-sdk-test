import os

import tangotest

_vnfs_dir = os.path.join(tangotest.__path__[0], 'vnfs')

vnfs = {
    'sniffer': {
        'source': os.path.join(_vnfs_dir, 'sniffer'),
        'interfaces': ['input', 'output']
    },
    'generator': {
        'source': os.path.join(_vnfs_dir, 'generator'),
        'interfaces': ['cp01']
    }
}

