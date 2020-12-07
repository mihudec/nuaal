from nuaal.Parsers import ParserModule
import timeit
import re

class CiscoIOSParser(ParserModule):
    """
    Child class of `ParserModule` designed for `cisco_ios` device type.
    """
    def __init__(self, verbosity=4, DEBUG=False):
        super(CiscoIOSParser, self).__init__(device_type="cisco_ios", verbosity=verbosity, DEBUG=DEBUG)

    def vlanGroup_check(self, vlanGroup):
        if isinstance(vlanGroup, list):
            if len(vlanGroup) > 0:
                vlanGroup = vlanGroup[0]
            else:
                vlanGroup = []
                return vlanGroup
        if isinstance(vlanGroup, str):
            if vlanGroup == "none":
                vlanGroup = []
                return vlanGroup
            vlanGroup = vlanGroup.split(",")
        elif isinstance(vlanGroup, int):
            vlanGroup = [str(vlanGroup)]
        return vlanGroup

    def trunk_parser(self, text):
        """
        Function specifically designed for parsing output of `show interfaces trunk` command.

        :param str text: Plaintext output of `show interfaces trunk` command.
        :return: List of dictionaries representing trunk interfaces.
        """
        start_time = timeit.default_timer()
        section_pattern = re.compile(pattern=r"(?:^Port.*$(?:\s^\S.*$)+)", flags=re.MULTILINE)
        sections = self.match_single_pattern(pattern=section_pattern, text=text)
        if len(sections) != 4:
            return []
        mode_pattern = re.compile(
            pattern=r"^(?P<interface>[A-Za-z]+\d+(\/\d+){0,2})\s+(?P<mode>\S+)\s+(?P<encapsulation>\S+)\s+(?P<status>\S+)\s+(?P<nativeVlan>\d+)",
            flags=re.MULTILINE
        )
        interface_pattern = re.compile(pattern=r"^(?P<interface>[A-Za-z]+\d+(\/\d+){0,2})\s+(?P<vlanGroup>(?:\d{1,4}(?:-\d{1,4})?,?)+)", flags=re.MULTILINE)
        mode = self.match_single_pattern(text=sections[0], pattern=mode_pattern)
        allowed = self.match_single_pattern(text=sections[1], pattern=interface_pattern)
        active = self.match_single_pattern(text=sections[2], pattern=interface_pattern)
        forwarding = self.match_single_pattern(text=sections[3], pattern=interface_pattern)
        trunks = []
        for trunk in mode:
            entry = dict(trunk)
            entry["allowed"] = self.vlanGroup_check([x["vlanGroup"] for x in allowed if x["interface"] == entry["interface"]])
            entry["active"] = self.vlanGroup_check([x["vlanGroup"] for x in active if x["interface"] == entry["interface"]])
            entry["forwarding"] = self.vlanGroup_check([x["vlanGroup"] for x in forwarding if x["interface"] == entry["interface"]])
            trunks.append(entry)
        self.logger.info(msg="Parsing of 'show interfaces trunk' took {} seconds.".format((timeit.default_timer()-start_time)))
        return trunks

    def parse_interfaces_switchport(self, text):
        entries = super(CiscoIOSParser, self).autoparse(text=text, command="show interfaces switchport")

        to_list_keys = ["trunk_enabled_vlans", "pruning_enabled_vlans"]
        for entry in entries:

            for key in to_list_keys:
                if isinstance(entry[key], str):
                    entry[key] = self.split_to_list(text=entry[key], delimiter=",")
        return entries

    def autoparse(self, text, command):
        """
        .. _autoparse:

        The main entry point for parsing, given just the ``text`` output and ``command`` it determines the proper way to parse the output and returns result.

        :param str text: Text output to be processed
        :param str command: Command used to generate ``text`` output. Based on this parameter, correct regex patterns are selected.
        :return: List of found entities, usually list of dictionaries
        """
        # Process Special Commands
        if command == "show interfaces trunk":
            return self.trunk_parser(text=text)
        elif command == "show interfaces switchport":
            return self.parse_interfaces_switchport(text=text)
        else:
            return super(CiscoIOSParser, self).autoparse(text=text, command=command)
