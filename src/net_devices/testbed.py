"""
    Module containing the TestBed class.
"""

from dataclasses import dataclass
from types import TracebackType
from typing import Dict, List, Optional, Type, Union
from genie.testbed import load
import unicon.core.errors
from net_devices import credentials

@dataclass
class Device:
    """
        Dataclass for devices
    
        Members
        -------
        hostname : str
            The hostname of the device
    """

    hostname: str

class TestBed:
    """ The TestBed class can be used to connect to create a list of
        devices on which to perform actions. Should be used as a
        context manager """
    
    def __init__(
        self,
        device_list: Optional[Union[List[str], str]] = None,
        connect: bool = True,
        log_output: bool = False
    ) -> None:
        """
            The initiator can be used to configure the devices to
            perform the actions on
        
            Parameters
            ----------
            device_list : Optional[List[str], str] [default=None]
                List of devices or a single device to add to the object
            
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

        # Set the devices, if given
        self.devices: List[Device] = list()
        if type(device_list) is list:
            self.devices = [Device(hostname=device) for device in device_list]
        elif type(device_list) is str:
            self.devices = [Device(hostname=device_list)]
        
        # Create empty testbed
        self.testbed: list = list()
        self.testbed_devices: Dict = {'devices': dict()}
    
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
        return self.testbed
    
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
            # TODO:
            # - Remove credentials
            # - Make sure the OS is retrieved
            self.testbed_devices['devices'][device.hostname.upper()] = {
                'ip': device.hostname.upper(),
                'port': 22,
                'protocol': 'ssh',
                'username': credentials['username'],
                'password': credentials['password'],
                'os': 'ios'
            }
    
    def add_devices(self, device_list: Union[List[str], str]) -> None:
        """
            Add one or multple devices to the object
        
            Parameters
            ----------
            devices : Union[List[str], str]
                A device or a list of devices to add
        
            Returns
            -------
            None
        """

        # If only one device is given, convert it to a list
        if type(device_list) is str:
            device_list = [device_list]
        
        # Check if this device is already in the list
        # TODO: Implement
        
        for device in device_list:
            self.devices.append(Device(hostname=device))
    
