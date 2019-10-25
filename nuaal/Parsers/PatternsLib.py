from nuaal.definitions import DATA_PATH
from nuaal.utils import get_logger, check_path
import os
import json
import re
import timeit


class PatternsLib:

    def __init__(self, device_type, verbosity=4, DEBUG=False):
        start_time = timeit.default_timer()
        self.device_type = device_type
        self.logger = get_logger(name="PatternsLib_{}".format(self.device_type), verbosity=verbosity, DEBUG=DEBUG)
        self.compiled_patterns = {}
        self._compile_all()
        total_time = round((timeit.default_timer() - start_time) * 1000, 3)
        self.logger.debug(msg="Initialization of PatternsLib took {} ms.".format(total_time))

    def _dir_modules(self):
        path = check_path(os.path.abspath(os.path.join(DATA_PATH, "patterns", self.device_type)))
        modules = [x for x in os.listdir(path) if x[-5:] == ".json"]
        self.logger.debug(msg="Found {} pattern modules for '{}'.".format(len(modules), self.device_type))
        module_paths = {}
        for module in modules:
            module_path = os.path.abspath(os.path.join(path, module))
            module_name = module[:-5].replace("_", " ")
            module_paths[module_name] = module_path
        return module_paths

    def _compile_pattern(self, pattern_dict):
        if not isinstance(pattern_dict, dict):
            self.logger.error(msg="Given parameter 'pattern_dict' is not a dictionary.")
        # Take pattern and flags from dictionary and return compiled pattern
        try:
            return re.compile(pattern=pattern_dict["pattern"], flags=pattern_dict["flags"])
        except Exception as e:
            # TODO: More specific exceptions
            self.logger.error(msg="Encountered exception when compiling pattern '{}'. Exception: {}".format(pattern_dict["pattern"], repr(e)))

    def _compile_module(self, module_path):
        start_time = timeit.default_timer()
        with open(module_path, mode="r") as file:
            pattern_data = json.load(file)

        compiled_pattern_data = {"command": pattern_data["command"]}
        for level in [x for x in pattern_data.keys() if "level" in x]:
            if isinstance(pattern_data[level], list):
                compiled_pattern_data[level] = []
                for pattern_dict in pattern_data[level]:
                    compiled_pattern_data[level].append(self._compile_pattern(pattern_dict=pattern_dict))
            elif isinstance(pattern_data[level], dict):
                compiled_pattern_data[level] = {}
                for key, patterns in pattern_data[level].items():
                    compiled_pattern_data[level][key] = []
                    for pattern_dict in patterns:
                        compiled_pattern_data[level][key].append(self._compile_pattern(pattern_dict=pattern_dict))
        self.logger.debug(msg="Compiling of patterns for '{}' took {} ms.".format(compiled_pattern_data["command"], round((timeit.default_timer() - start_time)*1000, 3)))
        return compiled_pattern_data

    def _compile_all(self):
        start_time = timeit.default_timer()
        for command, path in self._dir_modules().items():
            self.compiled_patterns[command] = {}
            compiled_module = self._compile_module(module_path=path)
            for level in [x for x in compiled_module.keys() if "level" in x]:
                self.compiled_patterns[command][level] = compiled_module[level]
        total_time = round((timeit.default_timer() - start_time)*1000, 3)
        self.logger.debug(msg="Compiling of all patterns for '{}' took {} ms.".format(self.device_type, total_time))
