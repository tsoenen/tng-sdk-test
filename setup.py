from setuptools import setup, find_packages

def readme():
    with open('README.rst') as f:
        return f.read()

setup(
    name="tangotest",
    version="0.1",
    description='5GTANGO SDK functional testing library',
    long_description=readme(),
    author='Askhat Nuriddinov',
    author_email='askhat.nuriddinov@ugent.be',
    packages=find_packages(),
    install_requires=[],
    include_package_data=True,
    zip_safe=False,
)
