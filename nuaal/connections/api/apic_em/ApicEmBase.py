from nuaal.connections.api import RestBase
from nuaal.definitions import DATA_PATH
import json
import requests
import re
import time


class ApicEmBase(RestBase):
    """
    Object providing access to Cisco's APIC-EM REST-API.
    """
    def __init__(self, url, username=None, password=None, api_base_path="/api/v1", verify_ssl=True, DEBUG=False):
        """

        :param url: URL of the APIC-EM, such as 'https://sandboxapicem.cisco.com'
        :param username: Username for authentication
        :param password: Password for authentication
        :param api_base_path: Base path for version-1 API
        :param verify_ssl: Enable/disable verification of SSL Certificate
        :param DEBUG: Enable/disable debugging output
        """
        super(ApicEmBase, self).__init__(url=url, username=username, password=password,
                                         api_base_path=api_base_path, verify_ssl=verify_ssl,
                                         DEBUG=DEBUG, con_type="APIC-EM")
        self.authorized = False

    def _authorize(self):
        """
        Function for obtaining authorization "Service Ticket" from the APIC-EM. This function is called when HTTP Status Code 401 (Unauthorized) is returned.

        :return: ``None``
        """
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
        """
        Function for loading credentials information stored in data/apicem_credentials.json file.

        :return: ``None``
        """
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
        """
        Function for storing credentials information in data/apicem_credentials.json file. This function is called after successfully obtaining Service Ticket

        :return: ``None``
        """
        self.logger.info(msg="Storing credentials.")
        with open(file="{}/apicem_credentials.json".format(DATA_PATH), mode="w") as f:
            json.dump({"username": self.username, "password": self.password, "serviceTicket": self.headers["X-Auth-Token"]}, f)

    def get(self, path, params=None):
        """
        Function providing HTTP GET method for retrieving data from APIC-EM API.

        :param path: Path of API resource, such as "/network-device". Each path must begin with "/" forward-slash character
        :param params: Dictionary of parameters for request, such as {"deviceId": "<ID of device in APIC-EM database>"}
        :return: Dictionary representation of response content under "response" key, eg. <request_response_object>.json()["response"] or ``None``
        """
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
        """
        Function providing HTTP POST method for sending data to APIC-EM API.

        :param path: Path of API resource, such as "/ticket". Each path must begin with "/" forward-slash character
        :param data: JSON string data payload
        :param params: Dictionary of parameters for request, such as {"deviceId": "<ID of device in APIC-EM database>"}
        :return: Dictionary representation of response content under "response" key, eg. <request_response_object>.json()["response"] or ``None``
        """
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

    def task_handler(self, taskId, timeout=2, max_retries=2):
        """
        Function for handling Task results, based on taskId.
        This function periodically queries APIC-EM for the results of given task until task is either completed or timeout is reached.
        Maximum time this function waits for result is (timeout * max_retries) seconds.

        :param taskId: ID of the task, returned by the APIC-EM after starting task.
        :param timeout: Number of seconds to wait after each unsuccessful request
        :param max_retries: Maximum number of requests.
        :return:
        """
        pass
        raise NotImplemented("This function is not yet implemented.")
