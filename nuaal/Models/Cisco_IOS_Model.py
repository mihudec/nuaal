from nuaal.connections.cli import Cisco_IOS_Cli
from nuaal.utils import int_name_convert, mac_addr_convert, interface_split, vlan_range_expander, vlan_range_shortener, Filter, OutputFilter
from nuaal.Models.BaseModels import BaseModel, DeviceBaseModel
import json
import copy


class CiscoIOSModel(DeviceBaseModel):
    """
    High-level abstraction model for Cisco IOS devices.
    """
    def __init__(self, cli_connection=None, DEBUG=False):
        """

        :param cli_connection: Instance of ``Cisco_IOS_Cli`` connection object.
        :param bool DEBUG: Enables/disables debugging output.
        """
        super(CiscoIOSModel, self).__init__(name="CiscoIOSCliModel", DEBUG=DEBUG)
        self.cli_connection = cli_connection
        self.physical_interfaces = ["FastEthernet", "GigabitEthernet", "TenGigabitEthernet"]

    def _map_interface(self, interface):
        """
        Internal function for changing the format of interface dictionary representation.

        :param dict interface: Dictionary representation of interface in a format provided by connection object's ``get_interfaces()`` function.
        :return: Dictionary representation interface in common format.
        """
        new_interface = copy.deepcopy(self.interface_model)
        new_interface["portName"] = interface["name"]
        new_interface["description"] = interface["description"]
        new_interface["interfaceType"] = "physical" if interface_split(interface["name"])[0] in self.physical_interfaces else "virtual"
        new_interface["status"] = interface["lineProtocol"]
        new_interface["adminStatus"] = interface["status"]
        new_interface["className"] = interface["hardware"]
        new_interface["macAddress"] = mac_addr_convert(interface["mac"])
        new_interface["duplex"] = interface["duplex"]
        new_interface["speed"] = interface["bandwidth"]
        new_interface["ipv4Address"] = interface["ipv4Address"]
        new_interface["ipv4Mask"] = interface["ipv4Mask"]
        new_interface["portMode"] = "routed" if interface["ipv4Address"] is not None else None

        return new_interface
    
    def _interface_update(self):
        """
        Internal function for retrieving needed data to build complete interface representation.

        :return: ``None``
        """

        if not self.cli_connection.is_alive:
            with self.cli_connection as device:
                access_vlans = device.get_vlans()
                trunks = device.get_trunks()
                interfaces = device.get_interfaces()
        else:
            access_vlans = self.cli_connection.get_vlans()
            trunks = self.cli_connection.get_trunks()
            interfaces = self.cli_connection.get_interfaces()

        #
        for interface in interfaces:
            name = interface["name"]
            self.interfaces[name] = self._map_interface(interface)

        #
        for vlan in access_vlans:
            vlan_id = vlan["id"]
            self.vlans[vlan_id] = copy.deepcopy(self.vlan_model)
            self.vlans[vlan_id]["name"] = vlan["name"]
            self.vlans[vlan_id]["vlanId"] = vlan["id"]
            self.vlans[vlan_id]["status"] = vlan["status"]

            for port in vlan["access_ports"]:

                port_long = int_name_convert(port)
                self.vlans[vlan_id]["untaggedPorts"].append(port_long)
                self.interfaces[port_long]["portMode"] = "access"
                self.interfaces[port_long]["untaggedVlanId"] = vlan_id

        for trunk in trunks:
            port = int_name_convert(trunk["interface"])
            self.interfaces[port]["portMode"] = "trunk"
            self.interfaces[port]["untaggedVlanId"] = trunk["nativeVlan"]
            self.interfaces[port]["taggedVlanIds"] = trunk["allowed"]
            if port not in self.vlans[trunk["nativeVlan"]]["untaggedPorts"]:
                self.vlans[trunk["nativeVlan"]]["untaggedPorts"].append(port)
            for vlan_id in vlan_range_expander(trunk["active"]):
                if vlan_id not in self.vlans[vlan_id]["taggedPorts"]:
                    self.vlans[vlan_id]["taggedPorts"].append(port)

    def get_interfaces(self):
        """
        Retrieves list of all interfaces in common format.

        :return: List of dictionaries.
        """
        if len(self.interfaces) == 0:
            self._interface_update()
        return self.interfaces

    def get_l3_interfaces(self):
        """
        Retrieves list of L3 (routed) interfaces in common format.

        :return: List of dictionaries.
        """
        if len(self.interfaces) == 0:
            self._interface_update()
        filter = Filter(required={"portMode": "routed"}, exact_match=True)
        l3_interfaces = filter.universal_cleanup(data=self.interfaces)
        return l3_interfaces

    def get_l2_interfaces(self):
        """
        Retrieves list of L2 (switched) interfaces in common format.


        :return: List of dictionaries.
        """
        if len(self.interfaces) == 0:
            self._interface_update()
        filter = Filter(required={"portMode": ["access", "trunk"]})
        l2_interfaces = filter.universal_cleanup(data=self.interfaces)
        return l2_interfaces

    def get_vlans(self):
        """
        Retrieves list of all configured VLANs on device in common format.

        :return: List of dictionaries.
        """
        if len(self.vlans) == 0:
            self._interface_update()
        return self.vlans

    def get_inventory(self):
        """
        Retrieves list of all installed HW parts on device in common format.

        :return: List of dictionaries.
        """
        device_inventory = []
        if not self.cli_connection.is_alive:
            with self.cli_connection as device:
                device_inventory = device.get_inventory()
        else:
            device_inventory = self.cli_connection.get_inventory()
        for raw_module in device_inventory:
            module = copy.deepcopy(self.inventory_model)
            module["name"] = raw_module["name"]
            module["description"] = raw_module["desc"]
            module["partNumber"] = raw_module["pid"]
            module["serialNumber"] = raw_module["sn"]
            module["version"] = raw_module["vid"]
            self.inventory.append(module)
        return self.inventory

