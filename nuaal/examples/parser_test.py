from nuaal.definitions import DATA_PATH
from nuaal.connections.cli import Cisco_IOS_Cli
import re
import json


provider = {
    "username": "mhudec",
    "password": "Mijujda3578&",
    "store_outputs": True,
    "enable": False
}

device1 = Cisco_IOS_Cli(ip="10.2.1.154", **provider)
device2 = Cisco_IOS_Cli(ip="10.2.1.1", **provider)

devices = [device1, device2]
for device in devices:
    device._connect()
    output = device._send_command("show spanning-tree")
    device.store_raw_output(command="show spanning-tree", raw_output=output)
    device.disconnect()