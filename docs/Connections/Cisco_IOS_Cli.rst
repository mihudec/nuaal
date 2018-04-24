Cisco_IOS_Cli
=============

``Cisco_IOS_Cli(CliBaseConnection)``

Object for interaction with network devices running Cisco IOS (or IOS XE) software via CLI interface.

``self.__init__(**kwargs)``

**Parameters:**

- **ip** - IPv4 address of network device
- **username** - Username for device login
- **password** - Password for user authentication
- **enable** - Boolean value, if True, the connection will operate in Privileged EXEC Mode. Might be required for some commands.
- **secret** - Enable secret password for entering device's Privileged EXEC Mode. Used together with enable=True.
- **parser** - Instance of CiscoIOSParser object to use for parsing commands output. By default, new parser instance is created for each Cisco_IOS_Cli object.
- **store_outputs** - Boolean value, if True, all commands outputs will be stored as TXT files in default data directory.
- **DEBUG** - Boolean value, if True, the self.logger will produce debugging output.

.. autoclass:: nuaal.connections.cli.Cisco_IOS_Cli.Cisco_IOS_Cli
    :members:
    :undoc-members:
    :show-inheritance:
