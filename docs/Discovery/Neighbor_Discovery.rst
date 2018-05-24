.. _Neighbor_Discovery:

Neighbor_Discovery
==================

This class performs discovery of network devices based on seed device's IP address. :ref:`IP_Discovery <IP_Discovery>`

.. note::

   In order for this discovery method to work, all network devices must have CDP (or LLDP) discovery protocol enabled on all links which connect to other devices.
   Also make sure that the advertised IP address is the IP address intended for device management and is reachable from the node you're running NUAAL on.

.. autoclass:: nuaal.Discovery.Neighbor_Discovery
    :members:
    :private-members:
    :undoc-members:
    :show-inheritance: