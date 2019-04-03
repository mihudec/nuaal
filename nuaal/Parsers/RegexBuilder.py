import re
import json
from nuaal.definitions import DATA_PATH
from nuaal.utils import get_logger
from nuaal.Parsers.PatternsLib_Old import Patterns

class RegexBuilder:
    def __init__(self, device_type, DEBUG=False):
        self.device_type = device_type
        self.logger = get_logger(name="RegexBuilder", DEBUG=DEBUG)

    def _flags_map(self, flag_str):
        if not isinstance(flag_str, str):
            self.logger.error(msg="Given parameter 'flag_str' is not a string.")
        flags_dict = {
            "multiline": 40,
            "dotall": re.DOTALL
        }
        try:
            return flags_dict[flag_str]
        except KeyError:
            self.logger.error(msg="Flag '{}' is not a recognized regex flag.".format(flag_str))
            return None

    def _compile_pattern(self, pattern_dict):
        if not isinstance(pattern_dict, dict):
            self.logger.error(msg="Given parameter 'pattern_dict' is not a dictionary.")
        # Take pattern and flags from dictionary and return compiled pattern
        try:
            return re.compile(pattern=pattern_dict["pattern"], flags=pattern_dict["flags"])
        except Exception as e:
            # TODO: More specific exceptions
            self.logger.error(msg="Encountered exception when compiling pattern '{}'. Exception: {}".format(pattern_dict["pattern"], repr(e)))

    def _decompile_pattern(self, pattern):
        if not isinstance(pattern, re._pattern_type):
            self.logger.error(msg="Given pattern is not a compiled re pattern.")
        pattern_string = pattern.pattern
        pattern_dict = {"pattern": pattern_string, "flags": 0}
        if "MULTILINE" in pattern.__str__():
            pattern_dict["flags"] = 40
        elif "DOTALL" in pattern.__str__():
            pattern_dict["flags"] = 48
        return pattern_dict

    def _store_json(self, pattern_data):
        command = pattern_data["command"]
        command_underscored = command.replace(" ", "_")
        with open(file="{}/patterns/{}/{}.json".format(DATA_PATH, self.device_type, command_underscored), mode="w") as file:
            try:
                json.dump(obj=pattern_data, fp=file, indent=2)
                self.logger.info(msg="Successfully stored JSON pattern in {}/{}.json".format(self.device_type, command_underscored))
            except Exception as e:
                self.logger.error(msg="Encountered exception when trying to save JSON pattern. Exception: {}".format(repr(e)))


if __name__ == '__main__':
    device_type = "cisco_ios"
    rb = RegexBuilder(device_type=device_type)

    pattern_dict = {"command": "show spanning-tree", "pattern": r"^VLAN0*(?P<vlan_id>\d+)\n^\s+Span.*?(?P<protocol>ieee|rstp|mst)\n^\s+Root ID\s+Priority\s+(?P<root_bid>\d+)\n^\s+Address\s+(?P<root_address>(?:[A-f0-9]{4}\.){2}[A-f0-9]{4})\n(?:(?:^\s+This bridge is the root\n)|(?:^\s+Cost\s+(?P<root_cost>\d+)\n^\s+Port\s+(?P<root_port_id>\d+) \((?P<root_port>\S*?)\))\n)^\s+Hello Time\s+(?P<root_hello_time>\d+).*?(?P<root_max_age>\d+).*?(?P<root_forward_delay>\d+).*?\n^\s*?Bridge ID\s+Priority\s+(?P<bridge_bid>\d+)\s+\(priority (?P<bridge_priority>\d+).*?(?P<sys_ext_id>\d+)\)\n^\s+Address\s+(?P<bridge_address>(?:[A-f0-9]{4}\.){2}[A-f0-9]{4})\n^\s+Hello Time\s+(?P<bridge_hello_time>\d+).*?(?P<bridge_max_age>\d+).*?(?P<bridge_forward_delay>\d+) sec\n\s+Aging Time\s+(?P<aging_time>\d+)(?: sec)?\n\s+Interface.*?\n^[-\s]*?\n(?P<interfaces>(?:^\S.*?\n)+)", "flags": re.MULTILINE}
    pattern = rb._compile_pattern(pattern_dict=pattern_dict)
    decompiled_pattern = rb._decompile_pattern(pattern=pattern)
    print(decompiled_pattern)
    pattern_dict.update(decompiled_pattern)
    print(pattern_dict)
    rb._store_json(pattern_data=pattern_dict)


