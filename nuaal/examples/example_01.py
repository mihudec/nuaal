from nuaal.connections.cli import Cisco_IOS_Cli
from nuaal.Writers import ExcelWriter
from nuaal.definitions import DATA_PATH
import json

# Start by creating a provider for device
# Provider is essentially a dict with required parameters
provider = {
    "ip": "192.168.100.106",    # IP address of device
    "username": "admin",        # Username to login
    "password": "cisco",        # Password to login
    "method": "ssh",            # Primary method of connection, either "ssh" or "telnet". If not given, defaults to "ssh"
    "DEBUG": True,              # If you want to see more detailed output, set this to True
    "enable": False,            # If you want to use commands that require Privileged EXEC Mode, set this to True
    "secret": "cisco",          # Password to enter Privileged EXEC Mode, only required with enable: True
    "store_outputs": True,      # If set to true, the raw text outputs will be stored in DATA_PATH\outputs\<device_IP_Address>\
}

# Create variable to store the outputs in
data = []

# Create connection
with Cisco_IOS_Cli(**provider) as device:
    device.get_version()
    device.get_inventory()
    data.append(device.data)

# Pretty print the results
print(json.dumps(data, indent=2))

# Writing results to excel file
writer = ExcelWriter()
# Create Excel file to write the results to
workbook = writer.create_workbook(path="{}".format(DATA_PATH), filename="example01.xlsx")
# Write the data
# Note that ExcelWriter.write_data() expects list of dictionaries, in which each dictionary represents one device
writer.write_data(workbook=workbook, data=data)
print("Data writen to {}\example01.xlsx".format(DATA_PATH))
