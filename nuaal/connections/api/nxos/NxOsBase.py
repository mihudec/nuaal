from nuaal.connections.api import RestBase
from nuaal.definitions import DATA_PATH
from nuaal.utils import check_path
import json
import os
import requests

class Cisco_NX_API(RestBase):
    def __init__(self, ip, username, password, verify_ssl=False, DEBUG=False):
        super(Cisco_NX_API, self).__init__(url="https://{}".format(ip),
                                           username=username,
                                           password=password,
                                           api_base_path="/ins",
                                           verify_ssl=verify_ssl,
                                           DEBUG=DEBUG,
                                           con_type="NXOS"
                                           )
    def _initialize(self):
        if self.verify_ssl == False:
            # Disable certificate warning
            try:
                requests.packages.urllib3.disable_warnings()
            except:
                self.logger.warning(msg="Failed to disable Certificate Warnings")
        self.common_headers["auth"] = (self.username, self.password)

    def craft_payload(self, commands):
        if isinstance(commands, str):
            commands = [x.strip() for x in commands.split(";")]
        commands = " ;".join(commands)
        payload = {
            "ins_api": {
                "version": "1.0",
                "type": "cli_show",
                "chunk": "0",
                "sid": "1",
                "input": commands,
                "output_format": "json"
            }
        }
        return json.dumps(payload)
    def test(self):
        self._initialize()
        payload = self.craft_payload("show cdp neighbors")
        response = self._response_handler(self._post(path="", data=payload))
        print(json.dumps(response, indent=2))


if __name__ == '__main__':
    device = Cisco_NX_API(ip="10.17.89.47",
                          username="admin",
                          password="1234Qwer",
                          DEBUG=True)
    device.test()
