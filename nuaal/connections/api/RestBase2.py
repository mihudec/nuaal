import timeit
import logging
import requests
from requests.auth import HTTPBasicAuth
from requests.exceptions import ConnectionError, Timeout
import json
import os
from nuaal.definitions import DATA_PATH
from nuaal.utils import get_logger


class RestBase2(object):
    """
    Parent class for all REST-like connections
    """
    def __init__(self, url, username=None, password=None, api_base_path=None, verify_ssl=False, DEBUG=False, con_type=None):
        """

        :param url: URL or IP address of the target machine
        :param username: Username for authentication
        :param password: Password for authentication
        :param api_base_path: Base path for the API resource, such as "/api/v1"
        :param verify_ssl: Enable SSL certificate verification. For self-signed certificates, set this to False
        :param DEBUG: Enable debugging output
        :param con_type: String representation of connection type, set by child classes
        """
        # Disable logging for external libraries
        logging.getLogger("requests").setLevel(logging.WARNING)
        logging.getLogger("urllib3").setLevel(logging.WARNING)

        self.url = url
        self.logger = get_logger(name="{}-{}".format(con_type if con_type else 'REST', self.url), DEBUG=DEBUG)
        self.username = username
        self.password = password
        self.api_base_path = api_base_path
        self.verify_ssl = verify_ssl
        self.DEBUG = DEBUG
        self.path_base = self.url + self.api_base_path
        self.headers = {"Content-type": "application/json"}
        self.common_headers = {"headers": self.headers, "verify": self.verify_ssl}
        self.authorized = False



    def _initialize(self):
        """
        Function for credentials loading and session preparation. Might be overwritten in child classes

        :return: ``None``
        """
        if not self.verify_ssl:
            # Disable certificate warning
            try:
                requests.packages.urllib3.disable_warnings()
            except:
                self.logger.warning(msg="Failed to disable Certificate Warnings")
        if self.username is None or self.password is None:
            self.logger.info(msg="No credentials provided, using cached instead.")
            if self._load_credentials():
                self.logger.info(msg="Credentials successfully loaded.")
            else:
                self.logger.info(msg="Failed to load valid credentials.")
        else:
            self._authorize()

    def _authorize(self):
        """
        Connection-specific function for handling authorization. Overridden by child classes

        :return: ``None``
        """
        pass

    def _store_data(self, data, path):
        path = os.path.join(DATA_PATH, path)
        try:
            with open(file=path, mode="w") as f:
                json.dump(obj=data, fp=f, indent=2)
        except Exception as e:
            self.logger.error(msg="Could not store data to file '{}'. Exception: {}".format(path, repr(e)))

    def _load_data(self, path):
        data = None
        path = os.path.join(DATA_PATH, path)
        try:
            with open(file=path, mode="r") as f:
                data = json.load(fp=f)
        except Exception as e:
            self.logger.error(msg="Could not load data from file '{}'. Exception: {}".format(path, repr(e)))
        finally:
            return data

    def _store_credentials(self):
        """
        Connection-specific function for handling authorization. Overridden by child classes

        :return: ``None``
        """
        pass

    def _load_credentials(self):
        """
        Connection-specific function for handling authorization. Overridden by child classes

        :return: ``None``
        """
        pass

    def request(self, method="GET", path="", raw=False, **kwargs):
        if not self.authorized:
            try:
                self._authorize()
            except Exception as e:
                self.logger.critical("Failed to authorize.")
            finally:
                if not self.authorized:
                    return None, None
        response = None
        url = self.path_base + path if path[0] == "/" else path
        try:
            response = requests.request(method=method, url=url, **kwargs, **self.common_headers)
        except requests.exceptions.ConnectionError:
            self.logger.critical(msg="Could not connect to {}".format(self.url))
        if raw:
            return response, response.status_code
        else:
            status_code = response.status_code
            if status_code == 200:
                return response.json(), status_code
