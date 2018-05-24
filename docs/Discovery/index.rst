.. _discovery:

*********
Discovery
*********

This module provides classes for network discovery. Discovery can be performed by two ways:

- Using one device as seed for discovery based on discovery protocols
- Using list of IP addresses of all devices in the network

.. note::

   Both mentioned ways rely on neighbor discovery protocols, which needs to be enabled in the network, such as CDP or LLDP. Without information provided by
   these protocols, it is impossible to reconstruct the network topology.

.. toctree::
   :maxdepth: 3

   IP_Discovery
   Neighbor_Discovery
   Topology