import os
import json
from nuaal.utils import get_logger

class Reader:
    def __init__(self):
        self.logger = get_logger("Reader")
        raise NotImplemented("This class currently being tested.")

    def filename_check(self, filename):
        if os.path.exists(filename):
            self.logger.debug(msg=f"Filename {filename} exists.")
            print(os.path.dirname(__file__))
            return filename
        else:
            cwd = os.path.dirname(__file__)
            filepath = os.path.join(cwd, filename)
            if os.path.exists(filepath):
                self.logger.debug(msg=f"Filename {filename} exists.")
                return os.path.abspath(filepath)
            else:
                self.logger.error(msg=f"Filename {filename} does not exist.")
                return None

    def load_json(self, filename):
        filename = self.filename_check(filename)
        data = None
        if filename:
            with open(filename, mode='r') as f:
                try:
                    data = json.load(f)
                except Exception as e:
                    self.logger.critical(msg=f"Failed to load JSON file, Exception: {e}")
                finally:
                    return data
        else:
            self.logger.critical(msg=f"Could not open file {filename}, file does not exist")
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
                    self.logger.critical(msg=f"Failed to load CSV file, Exception: {e}")
                    return lines

        else:
            self.logger.critical(msg=f"Could not open file {filename}, file does not exist")
            return lines

