# Connections

This section describes various ways to communicate with network devices in order to pull configuration information.

## CLI Connection

CLI Connections use widely used protocols, SSH and Telnet in order to communicate with network device. However, the CLI is made to be readable by humans, not so much by machines. In order to overcome this problem, we need to use some form of parsing the text outputs into more *machine-friendly* format. Nuaal contains parsing library which is able to produce structured JSON format from these text outputs. Each CLI Connection class is responsible for two key procedures:

1. Connecting to device, sending appropriate command and retrieve corresponding text output
2. Parse the text output by using *Parser* library and return data in JSON format

#### `CliBaseConnection(object)`

This class represents the base object, from which other (vendor specific classes) inherit. This class is basically a wrapper class around *Kirk Byers'* excellent library, [netmiko](https://github.com/ktbyers/netmiko). Even though the netmiko library already provides pretty straightforward and easy way to access network devices, the `CliBaseConnection` tries to handle multiple events which can arise, such as:

- Device is unreachable
- Fallback to Telnet if SSH is not supported by device (and vice-versa)
- Handles errors in outputs

Apart from the *'send command, receive output'*  this class also performs the parsing and storing outputs.

##### Base Functions

- `CliBaseConnection._connect_ssh(self)` - Initiates connection via SSH
- `CliBaseConnection._connect_telnet(self)` - Initiates connection via Telnet
- `CliBaseConnection._connect(self)` - Tries to connect to device via either SSH or Telnet. By default, SSH is preferred. At the end calls self._check_enable_level(*device*) with given *netmiko* device object.
- `CliBaseConnection._check_enable_level(self, device)` - This function verifies the given connection object *device*. This function makes sure, that the correct privilege level is active.
- `CliBaseConnection.disconnect(self)` - Wrapper function around *netmiko's* .disconnect(). Makes sure that the connection is properly closed.
- `CliBaseConnection._send_command(self)`
- `CliBaseConnection._command_handler(self, action)`
- `CliBaseConnection.store_raw_output(self, action)`

##### Get Functions

These functions handle retrieving *'show commands'* outputs and return parsed *dictionary* objects. Currently implemented functions are:

- `.get_vlans(self)` - Returns dictionary of configured VLANs with assigned ports
- `.get_inventory(self` - Returns dictionary of device hardware, such as line cards, power supplies, SFP modules etc. with Part Numbers (PN) and Serial Numbers (SN) for each component.
- `.get_interfaces(self` - Returns dictionary of all interfaces of device with all possible parameters, such as interface type, IP address, RX and TX statistics, dropped packets, interface load etc.
- `.get_portchannels(self` - Dictionary of logically bounded interfaces (*etherchannels* or *portchannels*) 
- `.get_license(self)` - Dictionary of license information.
- `.get_version(self)` - Function retrieving basic information about the device, such as device vendor, platform, installed software version, booted image name, uptime etc.
- `.get_mac_address_table(self)` - Dictionary representation of device's MAC Table, each entry contains MAC address, assigned VLAN and corresponding interface.
- `.get_arp(self)` - Dictionary representation of device's ARP Table, each entry contains mapping of an IP address to MAC address.

#### `Cisco_IOS_Cli(CliBaseConnection)`

Object for interaction with network devices running Cisco IOS (or IOS XE) software via CLI interface.

##### `self.__init__(**kwargs)`

**Parameters:**

- **ip** - IPv4 address of network device 
- **username** - Username for device login
- **password** - Password for user authentication
- **enable** - Boolean value, if *True*, the connection will operate in *Privileged EXEC Mode*. Might be required for some commands.
- **secret** - *Enable secret* password for entering device's *Privileged EXEC Mode*. Used together with `enable=True`.
- **parser** - Instance of `CiscoIOSParser` object to use for parsing commands output. By default, new parser instance is created for each `Cisco_IOS_Cli` object.
- **store_outputs** - Boolean value, if *True*, all commands outputs will be stored as TXT files in default *data* directory.
- **DEBUG** - Boolean value, if *True*, the `self.logger` will produce debugging output.