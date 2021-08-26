"""
    Module that contains the method to set the credentials for the
    net_devices package.
"""


def set_credentials(username: str, password: str) -> None:
    """ Method to set the credentials """

    # We import the credentials here to prevent a circular import
    from net_devices import credentials

    # Set the credentials
    credentials['username'] = username
    credentials['password'] = password
