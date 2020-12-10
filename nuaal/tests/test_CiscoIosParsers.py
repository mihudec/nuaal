import unittest
import pathlib
import json
from nuaal.Parsers import CiscoIOSParser

def jprint(data):
    print(json.dumps(obj=data, indent=2))

class TestCiscoIosParser(unittest.TestCase):

    PARSER = CiscoIOSParser()

    @staticmethod
    def get_text(test_file_name):
        test_file_path = pathlib.Path(__file__).parent.joinpath("resources/{}.txt".format(test_file_name))
        return test_file_path.read_text()

    @staticmethod
    def get_results(results_file_name):
        result_file_path = pathlib.Path(__file__).parent.joinpath("results/{}.json".format(results_file_name))
        return json.loads(result_file_path.read_text())

    def test_show_interfaces_switchport(self):
        command = "show interfaces switchport"
        test_file_bases = [
            "cisco_ios_show_interfaces_switchport_01",
            "cisco_ios_show_interfaces_switchport_02"
        ]
        for test_file_base in test_file_bases:
            with self.subTest(msg=test_file_base):
                text = self.get_text(test_file_name=test_file_base)
                want = self.get_results(results_file_name=test_file_base)
                have = self.PARSER.autoparse(text=text, command=command)
                jprint(have)
                self.assertEqual(want, have)

    def test_show_spanning_tree(self):
        command = "show spanning-tree"
        test_file_base = "cisco_ios_show_spanning_tree"
        with self.subTest(msg=test_file_base):
            text = self.get_text(test_file_name=test_file_base)
            want = self.get_results(results_file_name=test_file_base)
            have = self.PARSER.autoparse(text=text, command=command)
            # jprint(have)
            self.assertEqual(want, have)


if __name__ == '__main__':
    unittest.main()
