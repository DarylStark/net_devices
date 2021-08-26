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
        connect: bool = True,
        log_output: bool = False
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

            connect : bool [default=True]
                Determines if the devices should be connected while
                starting the context manager.

            log_output : bool [default=False]
                Determines if the output of the sessions should be
                written to STDOUT.

            Returns
            -------
            None
        """

        # Set the object variables
        self.connect = connect
        self.log_output = log_output

        # Create a empty list of devices
        self.devices: List[Device] = list()

        # Create empty testbed
        self.testbed: list = list()
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
            self.devices.append(devices)
        elif type(devices) is list:
            for device in devices:
                self.add_devices(device)

    def __enter__(self):
        """ Start of the context manager """

        # Create the Cisco TestBeds
        self.create_cisco_testbed()

        # Create a Cisco TestBed
        self.testbed = load(self.testbed_devices)

        # Connect, if we need to
        if self.connect:
            self.testbed.connect(
                init_exec_commands=[],
                init_config_commands=[],
                log_stdout=self.log_output)

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
