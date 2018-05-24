Cisco_IOS_Cli
=============
.. _Cisco_IOS_Cli:

This class provides low-level connection to Cisco networking devices running Cisco IOS and IOS XE. In order for this connection to work, SSH or Telnet
must be enabled on the target device. After creating connection object and connecting to the device using either Python's Context Manager or by calling
``_connect()`` method, you can start retrieving structured data by calling `get_` functions. To see other supported `get_` functions, please check out the
documentation page of the parent object :ref:`CliBaseConnection <CliBaseConnection>`.


Example usage:

.. code-block:: python

    >>> from nuaal.connections.cli import Cisco_IOS_Cli
    >>> # For further easier manipulation, create provider dictionary
    >>> provider = {
        "username": "admin",    # Username for authentication
        "password": "cisco",    # Password for authentication
        "enable": True,         # Whether or not enable Privileged EXEC Mode
        "secret": "cisco",      # Enable secret for entering Privileged EXEC Mode
        "store_outputs": True,  # Enables saving Plaintext output of commands
        "method": "ssh"         # Optional, defaults to "ssh"
    }
    >>>
    >>> # Create variable for storing data
    >>> data = None
    >>> # Establish connection using Context Manager
    >>> with Cisco_IOS_Cli(ip="192.168.1.1", **provider) as ios_device:
    >>>     # Run selected commands
    >>>     ios_device.get_interfaces()
    >>>     ios_device.get_vlans()
    >>>     ios_device.get_trunks()
    >>>     ios_device.get_version()
    >>>     ios_device.get_inventory()
    >>>     # Store data to variable
    >>>     data = ios_device.data
    >>> # Do other fancy stuff with data
    >>> print(data)

Defined ``get_*`` functions return output in JSON format (except for ``get_config()``). You can also send your own commands, such as:

.. code-block:: python

    >>> with Cisco_IOS_Cli(ip="192.168.1.1", **provider) as ios_device:
    >>>     ios_device._send_command(command="show version")

And you will receive Plaintext output of selected command.

.. autoclass:: nuaal.connections.cli.Cisco_IOS_Cli
    :members:
    :private-members:
    :undoc-members:
    :show-inheritance:
