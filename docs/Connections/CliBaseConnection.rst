CliBaseConnection
=================

``CliBaseConnection(object)``

.. autoclass:: nuaal.connections.cli.CliBaseConnection
    :members:
    :private-members:
    :undoc-members:
    :show-inheritance:

**Base Functions**


- ``._connect_ssh(self)`` - Initiates connection via SSH
- ``._connect_telnet(self)`` - Initiates connection via Telnet
- ``._connect(self)`` - Tries to connect to device via either SSH or Telnet. By default, SSH is preferred. At the end calls self._check_enable_level(device) with given netmiko device object.
- ``._check_enable_level(self, device)`` - This function verifies the given connection object device. This function makes sure, that the correct privilege level is active.
- ``.disconnect(self)`` - Wrapper function around netmiko's .disconnect(). Makes sure that the connection is properly closed.
- ``._send_command(self)``
- ``._command_handler(self, action)``
- ``.store_raw_output(self, action)``

**Get Functions**

These functions handle retrieving 'show commands' outputs and return parsed dictionary objects. Currently implemented functions are:

- ``.get_vlans(self)`` - Returns dictionary of configured VLANs with assigned ports
- ``.get_inventory(self)`` - Returns dictionary of device hardware, such as line cards, power supplies, SFP modules etc. with Part Numbers (PN) and Serial Numbers (SN) for each component.
- ``.get_interfaces(self)`` - Returns dictionary of all interfaces of device with all possible parameters, such as interface type, IP address, RX and TX statistics, dropped packets, interface load etc.
- ``.get_portchannels(self)`` - Dictionary of logically bounded interfaces (etherchannels or portchannels)
- ``.get_license(self)`` - Dictionary of license information.
- ``.get_version(self)`` - Function retrieving basic information about the device, such as device vendor, platform, installed software version, booted image name, uptime etc.
- ``.get_mac_address_table(self)`` - Dictionary representation of device's MAC Table, each entry contains MAC address, assigned VLAN and corresponding interface.
- ``.get_arp(self)`` - Dictionary representation of device's ARP Table, each entry contains mapping of an IP address to MAC address.
