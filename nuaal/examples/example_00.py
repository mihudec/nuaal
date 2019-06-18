from nuaal.connections.cli import Cisco_IOS_Cli
from nuaal.connections.cli.GetCliHandler import GetCliHandler
from nuaal.Models.Cisco_IOS_Model import CiscoIOSModel

provider = {
    "ip": "192.168.100.181",
    "username": "admin",
    "password": "cisco",
    "enable": True,
    "DEBUG": True,
    "store_outputs": True,
    "secret": "cisco"
}

device = GetCliHandler(device_type="cisco_ios", **provider)

model = CiscoIOSModel(cli_connection=device)
print(model.get_inventory())