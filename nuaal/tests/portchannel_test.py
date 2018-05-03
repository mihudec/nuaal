from nuaal.connections.cli import Cisco_IOS_Cli
from nuaal.utils import vlan_range_expander, vlan_range_shortener
import timeit
import json
provider = {
    "ip": "10.2.1.1",
    "username": "mhudec",
    "password": "Mijujda3578&",
    "enable": False,
    "store_outputs": True,
    "DEBUG": True
}

trunks = []
with Cisco_IOS_Cli(**provider) as device:
    trunks = device.get_trunks(expand_vlan_groups=False)
    pc = device.get_portchannels()
