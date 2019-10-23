import argparse
from tangotest.tangotools import create_vnv_test


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='Prepare tests for uploading to the V&V platform.')
    parser.add_argument('tests_path', help='The path to the directory with test files')
    parser.add_argument('ns_package_path', help='The path to the network service package')
    parser.add_argument('-t', '--test_package_path', help='The path to generated output folder')
    parser.add_argument('-p', '--probe_name', help='Probe name')

    args = parser.parse_args()
    create_vnv_test(**vars(args))
