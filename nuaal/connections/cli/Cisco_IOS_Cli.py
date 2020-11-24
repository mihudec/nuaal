from nuaal.connections.cli import CliBaseConnection
from nuaal.Parsers import CiscoIOSParser
from nuaal.utils import vlan_range_expander, vlan_range_shortener
from nuaal.definitions import DATA_PATH
import json
import threading
import queue
import datetime


class Cisco_IOS_Cli(CliBaseConnection):
    """
    Object for interaction with network devices running Cisco IOS (or IOS XE) software via CLI interface.
    """

    def __init__(
            self, ip=None, username=None, password=None,
            parser=None, secret=None, method="ssh", enable=False,
            store_outputs=False, DEBUG=False, verbosity=3,
            netmiko_params={}
    ):
        """

        :param ip: (str) IP address or FQDN of the device you're trying to connect to
        :param username: (str) Username used for login to device
        :param password: (str) Password used for login to device
        :param parser: (ParserModule) Instance of ParserModule class which will be used for parsing of text outputs.
        By default, new instance of ParserModule is created.
        :param secret: (str) Enable secret for accessing Privileged EXEC Mode
        :param method: (str) Primary method of connection, 'ssh' or 'telnet'. (Default is 'ssh')
        :param enable: (bool) Whether or not enable Privileged EXEC Mode on device
        :param store_outputs: (bool) Whether or not store text outputs of sent commands
        :param DEBUG: (bool) Enable debugging logging
        """
        super(Cisco_IOS_Cli, self).__init__(
            ip=ip, username=username, password=password,
            parser=parser if isinstance(parser, CiscoIOSParser) else CiscoIOSParser(),
            secret=secret, enable=enable, store_outputs=store_outputs,
            DEBUG=DEBUG, verbosity=verbosity, netmiko_params=netmiko_params
        )
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
            "get_interfaces_status": [
                "show interfaces status"
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
        """
        Function to get neighbors of the device with possibility to filter neighbors

        :param output_filter: (Filter) Instance of Filter class, used to filter neighbors, such as only "Switch" or "Router"
        :param strip_domain: (bool) Whether or not to strip domain names and leave only device hostname
        :return: List of dictionaries
        """
        command = "show cdp neighbors detail"
        raw_output = self._send_command(command=command)
        if not raw_output:
            return []
        if self.store_outputs:
            self.save_output(filename=command, data=raw_output)
        parsed_output = self.parser.autoparse(text=raw_output, command=command)
        if output_filter:
            parsed_output = output_filter.universal_cleanup(data=parsed_output)
        if strip_domain:
            for neighbor in parsed_output:
                neighbor["hostname"] = neighbor["hostname"].split(".")[0]
        self.data["neighbors"] = parsed_output
        return parsed_output

    def get_trunks(self, expand_vlan_groups=False):
        """
        Custom parsing function for output of "show interfaces trunk"

        :param expand_vlan_groups: (bool) Whether or not to expand VLAN ranges, for example '100-102' -> [100, 101, 102]
        :return: List of dictionaries
        """
        command = "show interfaces trunk"
        raw_output = self._send_command(command=command)
        if len(raw_output) == 0:
            self.data["trunk_interfaces"] = []
            return []
        if self.store_outputs:
            self.save_output(filename=command, data=raw_output)
        parsed_output = self.parser.trunk_parser(text=raw_output)
        if expand_vlan_groups:
            for trunk in parsed_output:
                trunk["allowed"] = vlan_range_expander(trunk["allowed"])
                trunk["active"] = vlan_range_expander(trunk["active"])
                trunk["forwarding"] = vlan_range_expander(trunk["forwarding"])
        self.data["trunk_interfaces"] = parsed_output
        return parsed_output

    def get_mac_address_table(self, vlan=None, interface=None):
        """
        Returns content of device MAC address table in JSON format. In Cisco terms, this represents the command `show mac address-table`.

        :param int vlan: Number of VLAN to get MAC addresses from
        :return: List of dictionaries.
        """
        return self._command_handler(action="get_mac_address_table")

    def get_interfaces_status(self):
        return self._command_handler(action="get_interfaces_status")

    def get_portchannels(self):
        return self._command_handler(action="get_portchannels")

    def get_config(self):
        """
        Function for retrieving current configuration of the device.

        :return str: Device configuration
        """
        command = "show running-config"
        raw_output = self._send_command(command=command)
        if self.store_outputs:
            self.save_output(filename=command, data=raw_output)
        self.data["running_config"] = raw_output
        return raw_output

    def get_auth_sessions(self):
        """

        :return:
        """
        commands = ["show authentication sessions"]
        return self._command_handler(commands=commands)



    def get_auth_sessions_intf(self, interface: str):
        """
        Function for retrieving 802.1X Auth Session on an interface

        :param str interface: Name of the interface to retrieve auth session from
        :return:
        """

        if interface is None:
            self.logger.error("This function needs interface parameter to be specified.")
            return []

        commands = [
            "show authentication sessions interface {} detail".format(interface),
            "show authentication sessions interface {}".format(interface)
        ]
        output = self._command_handler(commands=commands, return_raw=True)
        if output:
            return self.parser.autoparse(command="show authentication sessions interface", text=output)
        else:
            return []

