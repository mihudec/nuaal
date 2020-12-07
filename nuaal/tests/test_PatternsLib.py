import unittest
import pathlib
import json
from nuaal.Parsers import PatternsLib

def jprint(data):
    print(json.dumps(obj=data, indent=2))


class TestPatternsLib(unittest.TestCase):

    def test_cisco_ios_patters_are_valid(self):
        pl = None
        try:
            pl = PatternsLib(device_type="cisco_ios")
        except json.decoder.JSONDecodeError as e:
            msg = "Found invalid JSON file. Exception: {}".format(repr(e))
            self.fail(msg=msg)
        self.assertIsInstance(obj=pl, cls=PatternsLib)


if __name__ == '__main__':
    unittest.main()
