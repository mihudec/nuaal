from nuaal.utils import *
from nuaal.definitions import DATA_PATH
from nuaal.Parsers import Patterns
import json
import re
import timeit


class ParserModule(object):
    def __init__(self, device_type, DEBUG):
        self.device_type = device_type
        self.DEBUG = DEBUG
        self.logger = get_logger(name="ParserModule-{}".format(device_type), DEBUG=DEBUG)
        self.logger.info(msg="Creating ParserModule Object for {}".format(device_type))
        self.patterns = Patterns(device_type=device_type).get_patterns()

    def match_single_pattern(self, text, pattern):
        if not re.search(pattern=pattern, string=text):
            return []
        named_groups = [x for x in pattern.groupindex.keys() if isinstance(x, str)]
        if len(named_groups) == 0:
            return re.findall(pattern=pattern, string=text)
        else:
            entries = []
            for m in re.finditer(pattern=pattern, string=text):
                entry = {}
                for group_name in named_groups:
                    try:
                        entry[group_name] = int(m.group(group_name))
                    except (ValueError, TypeError):
                        entry[group_name] = m.group(group_name)
                    except IndexError:
                        entry[group_name] = None
                entries.append(entry)
            return entries

    def update_entry(self, orig_entry, new_entry):
        if not isinstance(orig_entry, dict) or not isinstance(new_entry, dict):
            raise TypeError()
        for k, v in new_entry.items():
            try:
                if orig_entry[k] is None:
                    orig_entry[k] = v
            except KeyError:
                orig_entry[k] = None
        self.logger.debug(msg="Updated entry {} based on {}".format(orig_entry, new_entry))
        return orig_entry

    def match_multi_pattern(self, text, patterns):
        named_groups = []
        entry = {}
        match_counter = 0
        start_time = timeit.default_timer()
        # Populate named_groups
        for pattern in patterns:
            for group_name in pattern.groupindex.keys():
                if isinstance(group_name, str) and group_name not in named_groups:
                    named_groups.append(group_name)
                    entry[group_name] = None
        self.logger.debug(msg="Found {} groups in patterns: {}".format(len(named_groups), named_groups))
        for pattern in patterns:
            match = re.search(pattern=pattern, string=text)
            if match:
                match_counter += 1
                pattern_match = {}
                for group_name in [x for x in pattern.groupindex.keys() if isinstance(x, str)]:
                    try:
                        pattern_match[group_name] = int(match.group(group_name))
                    except (TypeError, ValueError):
                        pattern_match[group_name] = match.group(group_name)
                entry = self.update_entry(entry, pattern_match)
                if None not in list(entry.values()):
                    break
        self.logger.debug(msg="MultiPatternMatch: Matched {} pattern(s) in {} miliseconds.".format(match_counter, (timeit.default_timer() - start_time)*1000))
        return entry

    def _level_zero(self, text, patterns):
        if not isinstance(text, str):
            self.logger.debug(msg="Level Zero: Expected string, got {}".format(type(text)))
            return []
        level_zero_outputs = []
        if not isinstance(patterns, list):
            patterns = list(patterns)
        for pattern in patterns:
            output = self.match_single_pattern(text=text, pattern=pattern)
            if not output:
                continue
            if len(output) == 0:
                continue
            else:
                level_zero_outputs = output
                break
        if len(level_zero_outputs) == 0:
            self.logger.warning(msg="Level Zero found no matches.")
        elif isinstance(level_zero_outputs[0], str):
            self.logger.debug(msg="Level Zero: Found {} matches without named groups.".format(len(level_zero_outputs)))
        elif isinstance(level_zero_outputs[0], dict):
            self.logger.debug(msg="Level Zero: Found {} matches without named groups.".format(len(level_zero_outputs)))
        else:
            self.logger.critical(msg="Level Zero: Unexpected event when trying to match {} with patterns {}.".format(text, patterns))
        return level_zero_outputs

    def _level_one(self, text, command):
        level_one_outputs = []
        level_zero_outputs = self._level_zero(text=text, patterns=self.patterns["level0"][command])
        if len(level_zero_outputs) == 0:
            self.logger.error(msg="Level Zero returned 0 outputs for command {}".format(command))
            return level_zero_outputs
        if command not in self.patterns["level1"].keys():
            self.logger.warning(msg="Command {} is not a 'level1' command.".format(command))
            return level_zero_outputs
        self.logger.debug(msg="Level Zero returned {} outputs.".format(len(level_zero_outputs)))
        if isinstance(level_zero_outputs[0], dict):
            for level_zero_entry in level_zero_outputs:
                entry = level_zero_entry
                for key, patterns in self.patterns["level1"][command].items():
                    try:
                        entry[key] = self._level_zero(text=level_zero_entry[key], patterns=patterns)
                    except KeyError:
                        self.logger.error(msg="Level Zero did not return entry with key {}.".format(key))
                        entry[key] = None
                    except TypeError as e:
                        self.logger.error(msg="Level Zero returned {} for key {}.".format(type(level_zero_entry[key]), key))
                        entry[key] = None
                level_one_outputs.append(entry)
        elif isinstance(level_zero_outputs[0], str):
            all_patterns = []
            for key, patterns in self.patterns["level1"][command].items():
                all_patterns += patterns
            for level_zero_entry in level_zero_outputs:
                entry = {}
                entry = self.match_multi_pattern(text=level_zero_entry, patterns=all_patterns)
                level_one_outputs.append(entry)
        return level_one_outputs

    def command_mapping(self, command):
        levels = ["level0", "level1"]
        max_level = None
        for level in levels:
            if command in list(self.patterns[level].keys()):
                max_level = level
        self.logger.debug(msg="Command '{}' level is: {}".format(command, level))
        return max_level

    def autoparse(self, text, command):
        command_level = self.command_mapping(command=command)
        parsed_output = None
        if command_level == "level0":
            return self._level_zero(text=text, patterns=self.patterns["level0"][command])
        elif command_level == "level1":
            return self._level_one(text=text, command=command)
        else:
            self.logger.critical(msg="AutoParse: Unknown level for command: '{}'".format(command))
