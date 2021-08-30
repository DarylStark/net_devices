"""
    Module containing the `Command` class. Can be used as a command to
    send to devices.
"""

from dataclasses import dataclass
from typing import Optional


@dataclass
class Command:
    """
        Used as a command to send to devices. Can make a difference
        between types of devices

        Members
        -------
        command : Optional[str] [default=None]
            The default command to send

        command_ios : Optional[str] [default=None]
            The command to send in case it is a Cisco IOS device

        command_ios_xr : Optional[str] [default=None]
            The command to send in case it is a Cisco IOS XR device

        command_ios_xe : Optional[str] [default=None]
            The command to send in case it is a Cisco IOS XE device

        command_nx_os : Optional[str] [default=None]
            The command to send in case it is a Cisco Nexus device
    """

    command: Optional[str] = None
    command_ios: Optional[str] = None
    command_ios_xr: Optional[str] = None
    command_ios_xe: Optional[str] = None
    command_nx_os: Optional[str] = None

    def set_commands(self) -> None:
        """ Method to set the commands for the different OS types. We
            fill in the commands that are None with the default
            command """

        if self.command_ios is None:
            self.command_ios = self.command

        if self.command_ios_xr is None:
            self.command_ios_xr = self.command

        if self.command_ios_xe is None:
            self.command_ios_xe = self.command

        if self.command_nx_os is None:
            self.command_nx_os = self.command
