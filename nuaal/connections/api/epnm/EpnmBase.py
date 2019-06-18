from nuaal.connections.api import RestBase
from requests.auth import HTTPBasicAuth
import json
from nuaal.definitions import DATA_PATH

class EpnmBase(RestBase):
    def __init__(self, url, username, password, api_base_path, verify_ssl, DEBUG=False):
        super(EpnmBase, self).__init__(url=url, username=username, password=password, api_base_path=api_base_path, verify_ssl=verify_ssl, DEBUG=DEBUG)

    def _authorize(self):
        self.common_headers = {"headers": self.headers, "auth": HTTPBasicAuth(self.username, self.password), "verify": self.verify_ssl}
        self._store_credentials()

    def _store_credentials(self):
        self.logger.info(msg="Storing credentials.")
        with open(file="{}/epnm_credentials.json".format(DATA_PATH), mode="w") as f:
            json.dump({"username": self.username, "password": self.password}, f)

    def _load_credentials(self):
        with open(file="{}/epnm_credentials.json".format(DATA_PATH), mode="r") as f:
            credentials = json.load(fp=f)
            for value in credentials.values():
                if value == "":
                    return False
            self.username = credentials["username"]
            self.password = credentials["password"]
            self.common_headers = {"headers": self.headers, "auth": HTTPBasicAuth(self.username, self.password), "verify": self.verify_ssl}
            return True

