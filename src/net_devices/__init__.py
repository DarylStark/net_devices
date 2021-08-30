"""
    Package to talk to network devices using Cisco Genie.
"""

from net_devices.initialize import initialize
from net_devices.command import Command

# Dictionary for the configuratoin
configuration = {
    'threading': {
        'max_threads': 128,
    },
    'default_credentials': {
        'username': None,
        'password': None
    }
}
