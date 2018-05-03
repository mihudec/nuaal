from nuaal.Models.BaseModels import BaseModel, DeviceBaseModel
from nuaal.connections.api.apic_em.ApicEmBase import ApicEmBase
from nuaal.utils import Filter
import copy

class ApicEmDeviceModel(DeviceBaseModel):
    """

    """
    def __init__(self, apic=None, object_id=None, filter=None, DEBUG=False):
        """

        :param apic:
        :param object_id:
        :param filter:
        :param DEBUG:
        """
        super(ApicEmDeviceModel, self).__init__(name="ApicEmDeviceModel", DEBUG=DEBUG)
        self.apic = apic if isinstance(apic, ApicEmBase) else ApicEmBase()
        self.filter = filter
        self.apic._initialize()
        self.apic_object_id = object_id
        self._initialize()

    def _initialize(self):
        """

        :return:
        """
        if self.apic_object_id is None:
            if "id" in self.filter.required.keys():
                self.apic_object_id = self.filter.required["id"]
            else:
                self.logger.debug(msg="No apic_object_id provided, trying to match based on filter.")
                try:
                    response = self.apic.get(path="/network-device")
                    response = self.filter.universal_cleanup(data=response)
                    if len(response) == 1:
                        self.logger.debug(msg="Exactly one object matched query. apic_object_id: '{}'".format(response[0]["id"]))
                        self.apic_object_id = response[0]["id"]
                    else:
                        self.logger.error(msg="Multiple ({}) APIC-EM objects match filter query. Please provide more specific query or enter object_id manually.".format(len(response)))
                except Exception as e:
                    self.logger.critical(msg="Unhandled Exception occurred while trying to initialize. Exception: {}".format(repr(e)))
        response = self.apic.get(path="/network-device/{}".format(self.apic_object_id))
        print(response)
        self.device_info["mgmtIpAddress"] = response["managementIpAddress"]
        self.device_info["hostname"] = response["hostname"]
        self.device_info["vendor"] = "Cisco"
        self.device_info["platform"] = response["platformId"]
        self.device_info["swVersion"] = response["softwareVersion"]
        self.device_info["uptime"] = response["upTime"]

    def get_interfaces(self):
        """

        :return:
        """
        if self.apic_object_id is None:
            self.logger.error(msg="Cannot query APIC-EM for interfaces, no device ID found.")
            return {}
        response = self.apic.get(path="/interface/network-device/{}".format(self.apic_object_id))
        for interface in response:
            print(interface)
            name = interface["portName"]
            self.interfaces[name] = copy.deepcopy(self.interface_model)
            self.interfaces[name]["description"] = interface["description"],
            self.interfaces[name]["interfaceType"] = interface["interfaceType"],
            self.interfaces[name]["className"] = interface["className"],
            self.interfaces[name]["status"] = interface["status"],
            self.interfaces[name]["macAddress"] = interface["macAddress"].upper(),
            self.interfaces[name]["adminStatus"] = interface["adminStatus"],
            self.interfaces[name]["speed"] = interface["speed"],
            self.interfaces[name]["portName"] = interface["portName"],
            self.interfaces[name]["untaggedVlanId"] = interface["nativeVlanId"],
            self.interfaces[name]["taggedVlanIds"] = interface["vlanId"],
            self.interfaces[name]["duplex"] = interface["duplex"],
            self.interfaces[name]["portMode"] = interface["portMode"],
            self.interfaces[name]["portType"] = interface["portType"],
            self.interfaces[name]["ipv4Mask"] = interface["ipv4Mask"],
            self.interfaces[name]["ipv4Address"] = interface["ipv4Address"],
            self.interfaces[name]["mediaType"] = interface["mediaType"],

        return self.interfaces

    def get_vlans(self):
        """

        :return:
        """
        raise NotImplemented
        if self.apic_object_id is None:
            self.logger.error(msg="Cannot query APIC-EM for interfaces, no device ID found.")
            return {}
        response = self.apic.get(path="/network-device/{}/vlan".format(self.apic_object_id))
        for vlan in response:
            print(response)

    def get_inventory(self):
        """

        :return:
        """
        if self.apic_object_id is None:
            self.logger.error(msg="Cannot query APIC-EM for interfaces, no device ID found.")
            return {}
        response = self.apic.get(path="/network-device/module", params={"deviceId": self.apic_object_id})
        for raw_module in response:
            print(raw_module)
            module = copy.deepcopy(self.inventory_model)
            module["name"] = raw_module["name"]
            module["description"] = raw_module["description"]
            module["partNumber"] = raw_module["partNumber"]
            module["serialNumber"] = raw_module["serialNumber"]
            module["version"] = raw_module["assemblyRevision"]

            self.inventory.append(module)
        return self.inventory

