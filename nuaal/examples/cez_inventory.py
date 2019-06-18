from nuaal.connections.cli import Cisco_IOS_Cli, CliMultiRunner
from nuaal.definitions import DATA_PATH
from nuaal.Writers import ExcelWriter
from operator import itemgetter

cisco_ips = [
    "10.19.55.213",
    "10.19.55.211",
    "10.19.55.207",
    "10.19.55.212",
    "10.19.55.202",
    "10.19.55.208",
    "10.19.55.203",
    "10.19.55.205",
    "10.19.55.206",
    "10.19.55.204",
    "10.19.55.201"
]
provider = {
    "username": "alef",
    "password": "poc",
    "store_outputs": True,
    "enable": True,
    "DEBUG": True
}
client = CliMultiRunner(provider=provider, ips=cisco_ips, DEBUG=True, actions=["get_version", "get_inventory", "get_config"])
client.run()
data = client.data
data = sorted(data, key=itemgetter("hostname"))
print(data)

writer = ExcelWriter()
workbook = writer.create_workbook(path=DATA_PATH, filename="cez_inventory.xlsx")
writer.write_data(workbook=workbook, data=data)
for device in data:
    hostname = device["hostname"]
    ip = device["ipAddress"]
    config = ""
    with open("{}\outputs\{}\show running-config.txt".format(DATA_PATH, ip), mode="r") as f:
        config = f.readlines()
    worksheet = workbook.add_worksheet(name=hostname)
    for i in range(len(config)):
        worksheet.write(i, 0, config[i])
workbook.close()

rad_ips = [
    "10.19.55.225",
    "10.19.55.226",
    "10.19.55.227",
    "10.19.55.228",
    "10.19.55.229",
    "10.19.55.230",
    "10.19.55.231",
    "10.19.55.232"
]
