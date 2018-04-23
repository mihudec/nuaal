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
                self.logger.info(msg=f"Successfully updated Service Ticket: {self.headers['X-Auth-Token']}")
                self._store_credentials()
        if status_code == 401:
            try:
                if response["response"]["errorCode"] == "INVALID_CREDENTIALS":
                    self.logger.critical(msg=f"Could not get Service Ticket. Reason: Invalid Credentials. Please provide valid credentials.")
                    self.authorized = False
            except Exception as e:
                self.logger.error(msg=f"_Authorize: Unhandled Exception occurred. Exception: {repr(e)}")

    def _load_credentials(self):
        with open(file=f"{DATA_PATH}/apicem_credentials.json", mode="r") as f:
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
        self.logger.info(msg=f"Storing credentials.")
        with open(file=f"{DATA_PATH}/apicem_credentials.json", mode="w") as f:
            json.dump({"username": self.username, "password": self.password, "serviceTicket": self.headers["X-Auth-Token"]}, f)

    def get(self, path, params=None):
        if not self.authorized:
            return None
        response, status_code = self._response_handler(self._get(path=path, params=params))
        if status_code in range(200, 208):
            return response["response"]
        elif status_code == 401:
            self.authorized = False
            self._authorize()
            return self.get(path=path, params=params)
        else:
            self.logger.error(msg=f"GET: Could not retrieve valid response for path '{path}'")
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
            self.logger.error(msg=f"GET: Could not retrieve valid response for path '{path}'")
            return None
