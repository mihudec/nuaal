import os
import json
from nuaal.utils import get_logger

class Reader:
    def __init__(self):
        self.logger = get_logger("Reader")
        raise NotImplemented("This class currently being tested.")

    def filename_check(self, filename):
        if os.path.exists(filename):
            self.logger.debug(msg="Filename {} exists.".format(filename))
            print(os.path.dirname(__file__))
            return filename
        else:
            cwd = os.path.dirname(__file__)
            filepath = os.path.join(cwd, filename)
            if os.path.exists(filepath):
                self.logger.debug(msg="Filename {} exists.".format(filename))
                return os.path.abspath(filepath)
            else:
                self.logger.error(msg="Filename {} does not exist.".format(filename))
                return None

    def load_json(self, filename):
        filename = self.filename_check(filename)
        data = None
        if filename:
            with open(filename, mode='r') as f:
                try:
                    data = json.load(f)
                except Exception as e:
                    self.logger.critical(msg="Failed to load JSON file, Exception: {}".format(repr(e)))
                finally:
                    return data
        else:
            self.logger.critical(msg="Could not open file {}, file does not exist".format(filename))
            return data

    def load_csv(self, filename, delimiter=","):
        filename = self.filename_check(filename)
        print(filename)
        lines = None
        if filename:
            with open(filename, mode='r') as f:
                try:
                    temp_lines = [x.split(delimiter) for x in f.readlines()]
                    lines = []
                    for line in temp_lines:
                        lines.append([x.strip() for x in line])
                    return lines
                except Exception as e:
                    self.logger.critical(msg="Failed to load CSV file, Exception: {}".format(repr(e)))
                    return lines

        else:
            self.logger.critical(msg="Could not open file {}, file does not exist".format(filename))
            return lines

