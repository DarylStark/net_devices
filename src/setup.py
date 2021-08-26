""" Module to install the `net_devices` library """

from setuptools import setup

setup(name = 'net_devices',
    version = '0.1',
    description = ('Wrapper around the Cisco Genie library to be able to use ' +
        'it as Context Manager'),
    url = '/var/adm/projects/development/net_devices/src',
    author = 'Daryl Stark',
    author_email = 'daryl.stark@integreater.nl',
    license = 'GNU GPLv3',
    zip_safe = False,
    packages = [ 'net_devices' ]
)
