# Net Devices

This Python 3 library can be used to use Cisco Genie as a Context Manager to parse commands. The package makes it possible to send commands to devices and specify which commands to run on Cisco IOS devices and Cisco IOS XR devices. This makes it easy to use the full potentionl of Cisco Genie without creating the boilerplate code to differentiate between devices and handle connection management.

## Install instructions

The installation of the library is fairly simple;

Clone the repository:

```bash
git clone https://github.com/Routz-Integreater/net_devices.git
```

Then, we create a Python Virtual Environment:

```bash
python -m venv env
```

The virtual environment is now configured in the folder `env`. Next, we activate the virtual environment:

```bash
source env/bin/activate
```

After that, we install this library into the environment

```bash
cd src/
pip3 install .
```

Now, you can use the library to play with your devices. You can, ofcourse, install it in your global Python packages.

## Usage instructions

The library is supposed to be used as library. The following code is an example on how to use it:

```python
from net_devices.testbed import TestBed, Device, DeviceType
from net_devices import Command
from net_devices import initialize

# Set the credentials. These will be used to connect to devices
initialize(username='user', pasword='cisco')

# Create a list with devices to use
device_list = [
    Device(hostname='RTR-IOS-A', device_type=DeviceType.CISCO_IOS),
    Device(hostname='RTR-IOS-B', device_type=DeviceType.CISCO_IOS),
    Device(hostname='RTR-XR-A', device_type=DeviceType.CISCO_IOS_XR),
    Device(hostname='RTR-XR-B', device_type=DeviceType.CISCO_IOS_XR),
]

# Create a net_devices TestBed. This can be used as context manager to
# make sure the net_devices library manages the connection, like
# connecting and disconnecting.
with TestBed(devices=device_list) as testbed:
    # Send a command to all devices
    interface_descriptions = testbed.parse('show interface descriptions')

    # Send a different command to Cisco IOS and XR devices
    routes = testbed.parse(
        Command(
            command_ios='show ip route',
            command_ios_xr='show route ipv4'
        )
    )

# Context manager is done, devices will disconnect automatically

# Print out the parsed results
print(interface_descriptions)
print(routes)
```
