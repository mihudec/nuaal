.. _cli_connection:

**************
CLI Connection
**************
CLI Connections use widely used protocols, SSH and Telnet in order to communicate with network device. However, the CLI is made to be readable by humans,
not so much by machines. In order to overcome this problem, we need to use some form of parsing the text outputs into more machine-friendly format.
Nuaal contains parsing library which is able to produce structured JSON format from these text outputs. Each CLI Connection class is responsible for two
key procedures:

1. Connecting to device, sending appropriate command and retrieve corresponding text output
2. Parse the text output by using :ref:`Parsers <parsers>` library and return data in JSON format.

Each device type is represented by specific object. For example, to connect to Cisco IOS (IOS XE) device, you need to use the :ref:`Cisco_IOS_Cli <Cisco_IOS_Cli>`
object. To make finding the correct object easier, you can use the `GetCliHandler` function.

.. autofunction:: nuaal.connections.cli.GetCliHandler.GetCliHandler


.. toctree::
   :maxdepth: 3

   CliBaseConnection
   Cisco_IOS_Cli
   CliMultiRunner