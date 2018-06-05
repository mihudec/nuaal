.. NUAAL documentation master file, created by
   sphinx-quickstart on Mon Apr 23 23:04:37 2018.
   You can adapt this file completely to your liking, but it should at least
   contain the root `toctree` directive.

Welcome to NUAAL's documentation!
=================================
This project aims to bring multiple ways of communicating with networking gear under one unified API. This should allow network engineers to gather
information about the network configuration in a fast and simple manner. In the early stage, this project focuses mainly on retrieving the information
from the devices, not so much on performing configuration changes.


**Installation**

You can install NUAAL either from Python package index PyPI or use the source code files available at GitHub_. To install NUAAL by pip, simply type
``pip install nuaal`` in your terminal.

**Usage**

For specific usage examples please check out appropriate section of this documentation. A good starting point describing how to get structured data directly
from routers and switches is :ref:`Cisco_IOS_Cli <Cisco_IOS_Cli>`.

.. _GitHub: https://github.com/mijujda/nuaal

.. toctree::
   :maxdepth: 3

   Connections/index
   Parsers/index
   Models/index
   Writers/index
   Discovery/index
   Utils/index

