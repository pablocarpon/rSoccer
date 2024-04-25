'''
#       Install Project Requirements 
'''
from setuptools import setup, find_packages

setup(name='rsoccer-gym',
    url="https://github.com/pablocarpon/rSoccer",
    description="VSS robot soccer gym environments",
    packages=[package for package in find_packages() if package.startswith("rsoccer_gym")],
    install_requires=['gymnasium', 'rc-robosim>=1.2.0', 'pygame', 'protobuf==3.20.0']
)
