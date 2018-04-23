from nuaal.connections.cli.CliBase import CliBaseConnection
from nuaal.Parsers.CiscoIOSParser import CiscoIOSParser
from nuaal.definitions import DATA_PATH
import json
import threading
import queue
import datetime

class Cisco_IOS_Cli(CliBaseConnection):
    def __init__(self, ip=None, username=None, password=None, parser=None, secret=None, method="ssh", enable=False, store_outputs=False, DEBUG=False):
        super(Cisco_IOS_Cli, self).__init__(ip=ip, username=username, password=password,
                                            parser=parser if isinstance(parser, CiscoIOSParser) else CiscoIOSParser(DEBUG=False),
                                            secret=secret, enable=enable, store_outputs=store_outputs, DEBUG=DEBUG)
        self.prompt_end = [">", "#"]
        self.ssh_method = "cisco_ios"
        self.telnet_method = "cisco_ios_telnet"
        self.primary_method = self.ssh_method if method == "ssh" else self.telnet_method
        self.secondary_method = self.telnet_method if method == "ssh" else self.ssh_method
        self.command_mappings = {
            "get_vlans": [
                "show vlan brief",
                "show vlan-switch brief"
            ],
            "get_mac_address_table": [
                "show mac address-table",
                "show mac-address-table"
            ],
            "get_neighbors": [
                "show cdp neighbors detail"
            ],
            "get_inventory": [
                "show inventory"
            ],
            "get_interfaces": [
                "show interfaces"
            ],
            "get_portchannels": [
                "show etherchannel summary"
            ],
            "get_arp": [
                "show ip arp"
            ],
            "get_license": [
                "show license"
            ],
            "get_version": [
                "show version"
            ]
        }

    def get_neighbors(self, output_filter=None, strip_domain=False):
        command = "show cdp neighbors detail"
        raw_output = self._send_command(command=command)
        if self.store_outputs:
            self.store_raw_output(command=command, raw_output=raw_output)
        parsed_output = self.parser.autoparse(text=raw_output, command=command)
        if output_filter:
            parsed_output = output_filter.universal_cleanup(data=parsed_output)
        if strip_domain:
            for neighbor in parsed_output:
                neighbor["hostname"] = neighbor["hostname"].split(".")[0]
        self.data["neighbors"] = parsed_output
        return parsed_output