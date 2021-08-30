"""
    Module that contains the method to set the config for the
    net_devices package.
"""

import logging


def initialize(
    username: str = None,
    password: str = None,
    max_threads: int = None
) -> None:
    """
        Function to initialize the package.

        Parameters
        ----------
        username : str [default=None]
            The default username to use to login

        password : str [default=None]
            The default password to use to login

        max_threads : str [default=None]
            The maximum number of threads to use to connect and run
            commands on devices.

        Returns
        -------
        None
    """

    # We import the configuration here to prevent a circular import
    from net_devices import configuration

    # Create a logger
    logger = logging.getLogger('initialize')

    # Set the credentials
    if username:
        logger.debug(f'Setting username to "{username}"')
        configuration['default_credentials']['username'] = username
    if password:
        logger.debug('Setting password')
        configuration['default_credentials']['password'] = password

    # Set the threads (if set)
    if max_threads:
        logger.debug(f'Setting max_threads to {max_threads}')
        configuration['threading']['max_threads'] = max_threads
