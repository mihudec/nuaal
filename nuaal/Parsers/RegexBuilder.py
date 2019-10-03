import re
import json
from nuaal.definitions import DATA_PATH
from nuaal.utils import get_logger

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
        if not isinstance(pattern, re.Pattern):
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

    pattern_dict = {
        "command": "show authentication sessions interface",
        "pattern": r"Interface:\s+(?P<interface>[A-Z][a-z][A-z]*?\d+(?:\/\d+)*)\n^\s+MAC Address:\s+(?P<mac_address>\S+)\n^\s+IP Address:\s+(?P<ip_address>\S+)\n^\s+User-Name:\s+(?P<user_name>\S+)\n^\s+Status:\s+(?P<status>.*?)\n^\s+Domain:\s+(?P<domain>\S+)\n^\s+Security Policy:\s+(?P<security_policy>.*?)\n^\s+Security Status:\s+(?P<security_status>.*?)\n^\s+Oper host mode:\s+(?P<oper_host_mode>.*?)\n^\s+Oper control dir:\s+(?P<oper_control_dir>.*?)\n^\s+Authorized By:\s+(?P<authorized_by>.*?)\n^\s+Vlan Policy:\s+(?P<vlan_policy>.*?)\n^\s+Vlan Group:\s+(?P<vlan_group>.*?)\n^\s+Session timeout:\s+(?P<session_timeout_server>\d+)s \(server\), Remaining: (?P<session_timeout_remaining>\d+)s\n^\s+Timeout action:\s+(?P<timeout_acction>.*?)\n^\s+Idle timeout:\s+(?P<idle_timeout>.*?)\n^\s+Common Session ID:\s+(?P<common_session_id>.*?)\n^\s+Acct Session ID:\s+(?P<acct_session_id>.*?)\n^\s+Handle:\s+(?P<handle>.*?)\n\nRunnable methods list:\n^\s+Method\s+State\n^\s+mab\s+(?P<mab>.*?)\n^\s+dot1x\s+(?P<dot1x>.*?)\n",
        "flags": re.MULTILINE
    }
    pattern = rb._compile_pattern(pattern_dict=pattern_dict)
    decompiled_pattern = rb._decompile_pattern(pattern=pattern)
    print(json.dumps(obj=decompiled_pattern, indent=2))
    pattern_dict.update(decompiled_pattern)
    print(pattern_dict)
{}

