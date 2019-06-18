.. _models:

******
Models
******
Models are high-level representation of network entities, such as devices, interfaces, network topologies etc. The main purpose of these *models*
is to provide single unified interface producing outputs of specified structure, no matter what kind of connection is used on the lower level. This helps
overcome issues with different dictionary structures, names of methods and more. Because each type of connection (CLI, REST API, Network Controller) provides
structured, but always slightly different format of data, there exists a model for each type of connection. This model then converts *connection specific*
data structures to those defined in BaseModel classes.

.. toctree::
   :maxdepth: 3

   BaseModel
   Cisco_IOS_Models
   ApicEmModels

Lets look at the following example:
In the first phase, we create two different connections, one being ``Cisco_IOS_Cli`` and the second being ``ApicEmBase``:

.. code-block:: python

   >>> import json
   >>> from nuaal.connections.cli import Cisco_IOS_Cli
   >>> from nuaal.connections.api import ApicEmBase

   >>> device1 = Cisco_IOS_Cli(**provider)
   >>> device2 = ApicEmBase(url="https://sandboxapicem.cisco.com")

Both of these 'devices' have completely different functions and data structures. In order to get interfaces of the *device1*, one would simply call:

.. code-block:: python

   >>> interfaces_1 = device1.get_interfaces()
   >>> # Print just the first interface for brevity
   >>> for interface in interfaces_1[:1]:
   >>> print(json.dumps(interface, indent=2))
   {
    "name": "FastEthernet0",
    "status": "up",
    "lineProtocol": "up",
    "hardware": "Fast Ethernet",
    "mac": "1cdf.0f45.52e0",
    "bia": "1cdf.0f45.52e0",
    "description": "MGMT",
    "ipv4Address": null,
    "ipv4Mask": null,
    "loadInterval": "5 minute",
    "inputRate": 1000,
    "inputPacketsInterval": 1,
    "outputRate": 1000,
    "outputPacketsInterval": 1,
    "duplex": "Full",
    "speed": null,
    "linkType": null,
    "mediaType": null,
    "sped": "100Mb/s",
    "mtu": 1500,
    "bandwidth": 100000,
    # .
    # <Output ommited>
    # .
    "outputBufferSwappedOut": 0
   }
   >>>

But for the *device2* (which isn't actually single device, but a controller with many devices), we would run:

.. code-block:: python

   >>> # Presume already knowing the id of device
   >>> interfaces_2 = device2.get(path="/interface/network-device/<deviceId>")
   >>> for interface in interfaces[:1]:
   >>> print(json.dumps(interface, indent=2))
   {
      "className": "SwitchPort",
      "description": "",
      "interfaceType": "Physical",
      "speed": "1000000",
      "adminStatus": "UP",
      "macAddress": "70:81:05:42:1e:b3",
      "ifIndex": "43",
      "status": "down",
      "voiceVlan": null,
      "portMode": "dynamic_auto",
      "portType": "Ethernet Port",
      "lastUpdated": "2018-05-02 14:53:01.67",
      "portName": "GigabitEthernet5/36",
      "ipv4Address": null,
      "ipv4Mask": null,
      "isisSupport": "false",
      "mappedPhysicalInterfaceId": null,
      "mappedPhysicalInterfaceName": null,
      "mediaType": "10/100/1000-TX",
      "nativeVlanId": "1",
      "ospfSupport": "false",
      "serialNo": "FOX1524GV2Z",
      "duplex": "AutoNegotiate",
      "series": "Cisco Catalyst 4500 Series Switches",
      "pid": "WS-C4507R+E",
      "vlanId": "1",
      "deviceId": "c8ed3e49-5eeb-4dee-b120-edeb179c8394",
      "instanceUuid": "0054cc51-ea16-471c-a634-5788220ff3f3",
      "id": "0054cc51-ea16-471c-a634-5788220ff3f3"
   }
   >>>

Apparently, both the provided information and data structure is different. To combine these data to single uniform database. This is where *models* come in.
We will continue based on previous example, right after defining connections: ``device1`` and ``device2``. From there on, we can create models:

.. code-block:: python

   >>> from nuaal.Models import Cisco_IOS_Model, ApicEmDeviceModel
   >>> model1 = Cisco_IOS_Model(cli_connection=device1)
   >>> model2 = ApicEmDeviceModel(apic=device2)


