"""
    Package to talk to network devices using Cisco Genie.
"""

from .initialize import initialize

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
