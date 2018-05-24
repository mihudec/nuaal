from nuaal.utils import get_logger
from nuaal.definitions import DATA_PATH
from nuaal.utils import int_name_convert, mac_addr_convert, interface_split, vlan_range_expander, vlan_range_shortener
from nuaal.utils import Filter


class BaseModel(object):
    """
    This is a parent object that all high-level API models inherit from.
    """
    def __init__(self, name=None, DEBUG=False):
        """

        :param name:
        :param DEBUG:
        """
        self.model_name = name if name else "BaseModel"
        self.DEBUG = DEBUG
        self.logger = get_logger(name="{}-Model".format(self.model_name), DEBUG=self.DEBUG)

    def __str__(self):
        return "{}-Model".format(self.model_name)

    def __repr__(self):
        return "{}-Model".format(self.model_name)

class DeviceBaseModel(BaseModel):
    """
    This is a parent object for device models.
    """
    def __init__(self, name="DeviceBaseModel", DEBUG=False):
        """

        :param name:
        :param DEBUG:
        """
        super(DeviceBaseModel, self).__init__(name=name, DEBUG=DEBUG)
        self.interfaces = {}
        self.vlans = {}
        self.inventory = []
        self.device_info = {
            "mgmtIpAddress": u"",
            "hostname": u"",
            "vendor": u"",
            "platform": u"",
            "swVersion": u"",
            "uptime": u""
        }
        self.interface_model = {
            "description": None,
            "interfaceType": None,
            "className": None,
            "status": None,
            "macAddress": None,
            "adminStatus": None,
            "speed": None,
            "portName": None,
            "untaggedVlanId": None,
            "taggedVlanIds": [],
            "duplex": None,
            "portMode": None,
            "portType": None,
            "ipv4Mask": None,
            "ipv4Address": None,
            "mediaType": None,
        }
        self.vlan_model = {
            "vlanId": "",
            "name": "",
            "status": "",
            "untaggedPorts": [],
            "taggedPorts": []
        }
        self.inventory_model = {
            "name": "",
            "description": "",
            "partNumber": "",
            "serialNumber": "",
            "version": ""
        }

    def get_interfaces(self):
        """

        :return:
        """
        raise NotImplemented("Function get_interfaces has not yet been implemented for model {}".format(self.model_name))

    def get_vlans(self):
        """

        :return:
        """
        raise NotImplemented("Function get_vlans has not yet been implemented for model {}".format(self.model_name))

    def get_neighbors(self):
        """

        :return:
        """
        raise NotImplemented("Function get_neighbors has not yet been implemented for model {}".format(self.model_name))