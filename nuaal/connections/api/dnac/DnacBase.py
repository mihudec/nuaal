from nuaal.connections.api.RestBase2 import RestBase2
from nuaal.definitions import DATA_PATH
from nuaal.utils import check_path
import json
import os
import copy
import requests
import re
import time


class DnacBase(RestBase2):

    def __init__(self, url, username=None, password=None, api_base_path="/api/v1", verify_ssl=True, DEBUG=False):
        """

        :param url: URL of the APIC-EM, such as 'https://sandboxapicem.cisco.com'
        :param username: Username for authentication
        :param password: Password for authentication
        :param api_base_path: Base path for version-1 API
        :param verify_ssl: Enable/disable verification of SSL Certificate
        :param DEBUG: Enable/disable debugging output
        """
        super(DnacBase, self).__init__(url=url, username=username, password=password,
                                       api_base_path=api_base_path, verify_ssl=verify_ssl,
                                       DEBUG=DEBUG, con_type="DNAC")
        self._initialize()

    def _authorize(self):
        if "X-Auth_Token" in self.headers.keys():
            del self.headers["X-Auth-Token"]
            self.common_headers = {"headers": self.headers, "verify": self.verify_ssl}
        response = None
        try:
            self.logger.debug(msg="Requesting new Auth Token.")
            response = requests.request(method="POST", url=self.url + "/api/system/v1/auth/token", auth=(self.username, self.password), **self.common_headers)
        except requests.exceptions.ConnectionError:
            self.logger.critical(msg="Could not connect to {}".format(self.url))
            self.authorized = False
            return False
        status_code = response.status_code
        if status_code == 401:
            self.logger.critical(msg="Could not get Auth Token. Reason: Invalid Credentials. Please provide valid credentials.")
            self.authorized = False
            return False
        if status_code == 200:
            response = response.json()
            if "Token" in response.keys():

                self.headers["X-Auth-Token"] = response["Token"]
                self.common_headers = {"headers": self.headers, "verify": self.verify_ssl}
                self.authorized = True
                self.logger.info(msg="Successfully updated Auth Token: {}".format(self.headers['X-Auth-Token']))
                self._store_credentials()
                return True

    def _load_credentials(self):
        """
        Function for loading credentials information stored in data/apicem_credentials.json file.

        :return: ``None``
        """
        credentials = self._load_data(path="dnac_credentials.json")
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
        data = {"username": self.username, "password": self.password, "serviceTicket": self.headers["X-Auth-Token"]}
        self._store_data(data=data, path="dnac_credentials.json")


if __name__ == '__main__':
    dnac = DnacBase(url="https://sandboxdnac.cisco.com", verify_ssl=True, DEBUG=True)
    dnac._authorize()
