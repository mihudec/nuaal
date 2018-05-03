===========
Connections
===========

This section describes various ways to communicate with network devices in order to pull configuration information.

**************
CLI Connection
**************
CLI Connections use widely used protocols, SSH and Telnet in order to communicate with network device. However, the CLI is made to be readable by humans, not so much by machines. In order to overcome this problem, we need to use some form of parsing the text outputs into more machine-friendly format. Nuaal contains parsing library which is able to produce structured JSON format from these text outputs. Each CLI Connection class is responsible for two key procedures:

1. Connecting to device, sending appropriate command and retrieve corresponding text output
2. Parse the text output by using Parser library and return data in JSON format

.. toctree::
   :maxdepth: 2

   CliBaseConnection
   Cisco_IOS_Cli