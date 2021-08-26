"""
    Module containing the TestBed class.
"""

from dataclasses import dataclass
from types import TracebackType
from typing import Dict, List, Optional, Type, Union
from genie.testbed import load
import unicon.core.errors
from net_devices import credentials
from enum import Enum
import logging
from concurrent.futures import ThreadPoolExecutor
from unicon.core.errors import ConnectionError
from genie.libs.parser.utils.common import ParserNotFound
from genie.metaparser.util.exceptions import SchemaEmptyParserError


class DeviceType(Enum):
    """ Enum for device types
        ---------
        CISCO_IOS
            Traditional Cisco IOS devices.

        CISCO_IOS_XR
            Cisco IOS XR devices.

        CISCO_IOS_XE
            Cisco IOS XE devices.

        CISCO_NX_OS
            Cisco Nexus devices.
    """
    CISCO_IOS = 'ios'
    CISCO_IOS_XR = 'iosxr'
    CISCO_IOS_XE = 'iosxe'
    CISCO_NX_OS = 'nxos'


@dataclass
class Device:
    """
        Dataclass for devices

        Members
        -------
        hostname : str
            The hostname of the device

        device_type : DeviceType [default=DeviceType.CISCO_IOS]
            The type of device:
    """

    hostname: str
    device_type: DeviceType = DeviceType.CISCO_IOS


class TestBed:
    """ The TestBed class can be used to connect to create a list of
        devices on which to perform actions. Should be used as a
        context manager """

    def __init__(
        self,
        devices: Optional[Union[List, str, Device]] = None,
        auto_connect: bool = True,
        log_output: bool = False,
        use_testbed: bool = False
    ) -> None:
        """
            The initiator can be used to configure the devices to
            perform the actions on

            Parameters
            ----------
            devices : Optional[List[str], str] [default=None]
                List of devices or a single device to add to the
                object. Can be a single device as a string, a single
                device as Device-object, a list of strings or a list
                of Device-objects.

            auto_connect : bool [default=True]
                Determines if the devices should be connected while
                starting the context manager.

            log_output : bool [default=False]
                Determines if the output of the sessions should be
                written to STDOUT.

            use_testbed: bool [default=False]
                Determines how to connect and execute commands. If it
                is set to True, the Cisco Testbed is used. If set to
                False, we use a own ThreadPoolExecutor. The former is
                more standadized, but if one device fail, they all
                fail.

            Returns
            -------
            None
        """

        # Create a logger
        self.logger = logging.getLogger('TestBed')

        # Set the object variables
        self.auto_connect = auto_connect
        self.log_output = log_output
        self.use_testbed = use_testbed

        # Create a empty list of devices
        self.devices: List[Device] = list()

        # Create empty testbed
        self.testbed = None
        self.testbed_devices: Dict = {'devices': dict()}

        # Add the devices
        if devices:
            self.add_devices(devices)

    def add_devices(self, devices: Union[List, str, Device]) -> None:
        """
            Add one or multple devices to the object

            Parameters
            ----------
            devices : Optional[List[str], str] [default=None]
                List of devices or a single device to add to the
                object. Can be a single device as a string, a single
                device as Device-object, a list of strings or a list
                of Device-objects.

            Returns
            -------
            None
        """

        # Check the type of 'devices' that is given and do the
        # appropiate action
        if type(devices) is str:
            self.add_devices(Device(hostname=devices))
        elif type(devices) is Device:
            self.logger.info(f'Adding device "{devices.hostname}"')
            self.devices.append(devices)
        elif type(devices) is list:
            for device in devices:
                self.add_devices(device)

    def load_testbed(self):
        """ Method that loaded the testbed-object """
        if self.testbed is None:
            # Create the Cisco TestBeds
            self.create_cisco_testbed()

            # Load the devices
            self.testbed = load(self.testbed_devices)

    def connect_device(self, device) -> None:
        """
            Method to connect to a device.

            Parameters
            ----------
            device
                The device to connect to

            Returns
            -------
            None
        """
        self.logger.info(f'Connecting to {device.name}')
        try:
            device.connect(
                init_exec_commands=[],
                init_config_commands=[],
                log_stdout=self.log_output)
        except ConnectionError:
            self.logger.error(f'Couldn\'t connect to device {device.name}')

    def parse_command(self, arguments: dict) -> None:
        """
            Method to run a parse command on a device

            Parameters
            ----------
            arguments
                The arguments given to the method. Is done by a dict
                because that is the way the ThreadPoolExecutor works.
                Should contain the following keys:
                - 'device': the device object to run it on
                - 'command': the command to run
                - 'return_dict': a dict where we can place the return
                   values

            Returns
            -------
            None
        """

        try:
            device = arguments['device']
            command = arguments['command']
            return_dict = arguments['return_dict']
        except KeyError:
            return None

        self.logger.info(
            f'Running the command "{command}" on ' +
            f'device "{device.name}"')

        if device.is_connected():
            try:
                return_dict[device.name] = device.parse(command)
            except (ParserNotFound, SchemaEmptyParserError):
                return_dict[device.name] = None
        else:
            self.logger.warning(
                f'Skipping device "{device}" because it is not connected')

    def parse(self, command: str, use_testbed: Optional[bool] = None) -> dict:
        """
            Method to run a parsed command.

            Parameters
            ----------
            command : str
                The command to send.

            use_testbed : Optional[bool] [default=None]
                Determines how to connect and execute commands. If it
                is set to True, the Cisco Testbed is used. If set to
                False, we use a own ThreadPoolExecutor. The former is
                more standadized, but if one device fail, they all
                fail. By default, the configured value for the object
                is used.

            Returns
            -------
            dict:
                The dict that contains the parsed commands
        """

        # Set the method to connect
        if use_testbed is None:
            use_testbed = self.use_testbed

        # Check if the Cisco TestBed is created
        if use_testbed:
            # Connect using the Cisco TestBed
            self.logger.info(
                'Sending a parsing-command to all devices using the Cisco ' +
                'TestBed')
            return self.testbed.parse(command)
        else:
            # Connect device one by one
            self.logger.info(
                'Sending a parsing-command to all devices one by one')

            # Empty return dict
            return_dict = dict()

            # Generate the arguments
            devices = [
                {
                    'device': obj,
                    'command': command,
                    'return_dict': return_dict
                }
                for device, obj in self.testbed.devices.items()
            ]

            # Start the threads
            with ThreadPoolExecutor(max_workers=3) as executor:
                executor.map(self.parse_command, devices)

            self.logger.info('Done with running the parse commands')

            return return_dict

    def connect(self, use_testbed: Optional[bool] = None) -> None:
        """
            Method to connect to the devices

            Parameters
            ----------
            use_testbed : Optional[bool] [default=None]
                Determines how to connect and execute commands. If it
                is set to True, the Cisco Testbed is used. If set to
                False, we use a own ThreadPoolExecutor. The former is
                more standadized, but if one device fail, they all
                fail. By default, the configured value for the object
                is used.

            Returns
            -------
            Return values
        """

        # Load the testbed
        self.load_testbed()

        # Set the method to connect
        if use_testbed is None:
            use_testbed = self.use_testbed

        # Check if the Cisco TestBed is created
        if use_testbed:
            # Connect using the Cisco TestBed
            self.logger.info(
                'Connecting to all devices using the Cisco TestBed')
            self.testbed.connect(
                init_exec_commands=[],
                init_config_commands=[],
                log_stdout=self.log_output)
        else:
            # Connect device one by one
            self.logger.info('Connecting to all devices one by one')
            devices = [obj for device, obj in self.testbed.devices.items()]

            with ThreadPoolExecutor(max_workers=3) as executor:
                executor.map(self.connect_device, devices)

    def __enter__(self):
        """ Start of the context manager """

        # Load the testbed
        self.load_testbed()

        # Connect, if we need to
        if self.auto_connect:
            self.connect()

            # Return the testbed
        return self

    def __exit__(self,
                 exception_type: Optional[Type[BaseException]],
                 exception_value: Optional[BaseException],
                 traceback: Optional[TracebackType]) -> bool:
        """ Context manager is done! """
        try:
            self.testbed.disconnect()
        except unicon.core.errors.SubCommandFailure:
            pass

        # If 'type' is None, there was no error so we can return True.
        # Otherwise, False is returned and the exception is passed
        # through
        return exception_type is None

    def create_cisco_testbed(self) -> None:
        """ Method to create the Cisco TestBed """

        # Add all devices to the list for the Genie Testbed
        for device in self.devices:
            self.testbed_devices['devices'][device.hostname.upper()] = {
                'ip': device.hostname.upper(),
                'port': 22,
                'protocol': 'ssh',
                'username': credentials['username'],
                'password': credentials['password'],
                'os': device.device_type.value
            }
