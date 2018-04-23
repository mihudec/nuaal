from nuaal.Parsers import ParserModule
import timeit
import re

class CiscoIOSParser(ParserModule):
    def __init__(self, DEBUG=False):
        super(CiscoIOSParser, self).__init__(device_type="cisco_ios", DEBUG=DEBUG)

    def trunk_parser(self, text):
        start_time = timeit.default_timer()
        section_pattern = re.compile(pattern=r"(?:^Port.*$(?:\s^\S.*$)+)", flags=re.MULTILINE)
        mode, allowed, active, forwarding = self.match_single_pattern(pattern=section_pattern, text=text)
        mode_pattern = re.compile(
            pattern=r"^(?P<interface>[A-Za-z]+\d+(\/\d+){0,2})\s+(?P<mode>\S+)\s+(?P<encapsulation>\S+)\s+(?P<status>\S+)\s+(?P<native_vlan>\d+)",
            flags=re.MULTILINE
        )
        interface_pattern = re.compile(pattern=r"^(?P<interface>[A-Za-z]+\d+(\/\d+){0,2})\s+(?P<vlan_group>(?:\d{1,4}(?:-\d{1,4})?,?)+)", flags=re.MULTILINE)
        mode = self.match_single_pattern(text=mode, pattern=mode_pattern)
        allowed = self.match_single_pattern(text=allowed, pattern=interface_pattern)
        active = self.match_single_pattern(text=active, pattern=interface_pattern)
        forwarding = self.match_single_pattern(text=forwarding, pattern=interface_pattern)
        trunks = []
        for trunk in mode:
            entry = dict(trunk)
            try:
                entry["allowed"] = [x["vlan_group"] for x in allowed if x["interface"] == entry["interface"]][0].split(",")
            except AttributeError:
                entry["allowed"] = [x["vlan_group"] for x in allowed if x["interface"] == entry["interface"]][0]
            try:
                entry["active"] = [x["vlan_group"] for x in active if x["interface"] == entry["interface"]][0].split(",")
            except AttributeError:
                entry["active"] = [x["vlan_group"] for x in active if x["interface"] == entry["interface"]][0]
            try:
                entry["forwarding"] = [x["vlan_group"] for x in forwarding if x["interface"] == entry["interface"]][0].split(",")
            except AttributeError:
                entry["forwarding"] = [x["vlan_group"] for x in forwarding if x["interface"] == entry["interface"]][0]
            trunks.append(entry)
        self.logger.info(msg=f"Parsing of 'show interfaces trunk' took {(timeit.default_timer()-start_time)} seconds.")
        return trunks
