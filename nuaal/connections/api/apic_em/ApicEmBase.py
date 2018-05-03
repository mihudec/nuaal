from nuaal.connections.api import RestBase
from nuaal.definitions import DATA_PATH
import json
import requests

class ApicEmBase(RestBase):
    def __init__(self, url, username=None, password=None, api_base_path="/api/v1", verify_ssl=True, DEBUG=False):
        super(ApicEmBase, self).__init__(url=url, username=username, password=password,
                                         api_base_path=api_base_path, verify_ssl=verify_ssl,
                                         DEBUG=DEBUG, con_type="APIC-EM")
        self.authorized = False

    def _authorize(self):
        if "X-Auth_Token" in self.headers.keys():
            del self.headers["X-Auth-Token"]
            self.common_headers = {"headers": self.headers, "verify": self.verify_ssl}
        response, status_code = self._response_handler(self._post(path="/ticket", data=json.dumps({"username": self.username, "password": self.password})))

        if status_code == 200:
            if "serviceTicket" in response["response"].keys():
                self.headers["X-Auth-Token"] = response["response"]["serviceTicket"]
                self.common_headers = {"headers": self.headers, "verify": self.verify_ssl}
                self.authorized = True
                self.logger.info(msg="Successfully updated Service Ticket: {}".format(self.headers['X-Auth-Token']))
                self._store_credentials()
        if status_code == 401:
            try:
                if response["response"]["errorCode"] == "INVALID_CREDENTIALS":
                    self.logger.critical(msg="Could not get Service Ticket. Reason: Invalid Credentials. Please provide valid credentials.")
                    self.authorized = False
            except Exception as e:
                self.logger.error(msg="_Authorize: Unhandled Exception occurred. Exception: {}".format(repr(e)))

    def _load_credentials(self):
        with open(file="{}/apicem_credentials.json".format(DATA_PATH), mode="r") as f:
            credentials = json.load(fp=f)
            for value in credentials.values():
                if value == "":
                    return False
            self.username = credentials["username"]
            self.password = credentials["password"]
            self.headers["X-Auth-Token"] = credentials["serviceTicket"]
            self.common_headers = {"headers": self.headers, "verify": self.verify_ssl}
            self.authorized = True
            return True

    def _store_credentials(self):
        self.logger.info(msg="Storing credentials.")
        with open(file="{}/apicem_credentials.json".format(DATA_PATH), mode="w") as f:
            json.dump({"username": self.username, "password": self.password, "serviceTicket": self.headers["X-Auth-Token"]}, f)

    def get(self, path, params=None):
        if not self.authorized:
            self.logger.error(msg="Connection is not authorized")
            return None
        response, status_code = self._response_handler(self._get(path=path, params=params))
        if status_code in range(200, 208):
            return response["response"]
        elif status_code == 401:
            self.authorized = False
            self._authorize()
            return self.get(path=path, params=params)
        else:
            self.logger.error(msg="GET: Could not retrieve valid response for path '{}'".format(path))
            return None

    def post(self, path, data, params):
        if not self.authorized:
            return None
        response, status_code = self._response_handler(self._post(path=path, data=data, params=params))
        if status_code in range(200, 208):
            return response["response"]
        elif status_code == 401:
            self.authorized = False
            self._authorize()
            return self.get(path=path, params=params)
        else:
            self.logger.error(msg="GET: Could not retrieve valid response for path '{}'".format(path))
            return None

if __name__ == '__main__':
    with ApicEmBase(url="https://sandboxapicem.cisco.com", DEBUG=True) as apic:

        print(json.dumps(apic.get(path="/interface/network-device/26450a30-57d8-4b56-b8f1-6fc535d67645"), indent=2))