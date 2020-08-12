import timeit
import logging
import requests
from requests.auth import HTTPBasicAuth
from requests.exceptions import ConnectionError, Timeout
import json
from nuaal.definitions import DATA_PATH
from nuaal.utils import get_logger

class RestBase(object):
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

    def __enter__(self):
        """Allow usage of Python Context Manager"""
        self._initialize()
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        """Allow usage of Python Context Manager"""
        pass

    def _initialize(self):
        """
        Function for credentials loading and session preparation. Might be overwritten in child classes

        :return: ``None``
        """
        if self.verify_ssl == False:
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

    def _get(self, path, params=None):
        """
        Wrapper function for GET method of the requests library

        :param path: Path of the API resource used in URL
        :param params: Parameters for the request
        :return: Instance of ``requests`` response object
        """
        response = None
        try:
            self.logger.debug(msg="_GET: Path: '{}', Params: '{}'".format(path, params))
            url = self.path_base + path
            if params:
                response = requests.get(url=url, **self.common_headers, params=params)
            else:
                response = requests.get(url=url, **self.common_headers)
        except ConnectionError:
            self.logger.critical(msg="_GET: Could not connect to {}. Wrong address?".format(url))
        except Exception as e:
            self.logger.error(msg="_GET: Encountered unhandled Exception: {}".format(repr(e)))
        finally:
            return response

    def _post(self, path, data=None, files=None, params=None):
        """
        Wrapper function for POST method of the requests library

        :param path: Path of the API resource used in URL
        :param data: Data payload for POST request. JSON string
        :param dict files: Dictionary with files to upload
        :param params: Parameters for the request
        :return: Instance of ``requests`` response object
        """
        response = None
        args = {}
        if data:
            args["data"] = data
        if files:
            args["files"] = files
            del self.common_headers["headers"]["Content-type"]
        if params:
            args["params"] = params
        try:
            self.logger.debug(msg="_POST: Path: '{}', Data: '{}', Params: '{}'".format(path, data, params))
            response = requests.post(url=self.path_base + path, **args, **self.common_headers)
        except ConnectionError:
            self.logger.critical(msg="_POST: Could not connect to {}. Wrong address?".format(self.url))
        except Exception as e:
            self.logger.error(msg="_POST: Encountered unhandled Exception: {}".format(repr(e)))
        finally:
            self.common_headers["headers"]["Content-type"] = "application/json"
            return response

    def _delete(self, path, params):
        """
        Wrapper function for DELETE method of the requests library

        :param path: Path of the API resource used in URL
        :param params: Parameters for the request
        :return: Instance of ``requests`` response object
        """
        response = None
        try:
            self.logger.debug(msg="_DELETE: Path: '{}', Params: '{}'".format(path, params))
            if params:
                response = requests.delete(url=self.path_base + path, **self.common_headers, params=params)
            else:
                response = requests.delete(url=self.path_base + path, **self.common_headers)
        except ConnectionError:
            self.logger.critical(msg="_DELETE: Could not connect to {}. Wrong address?".format(self.url))
        except Exception as e:
            self.logger.error(msg="_DELETE: Encountered unhandled Exception: {}".format(repr(e)))
        finally:
            return response

    def _put(self, path, data=None, files=None, params=None):
        """
        Wrapper function for PUT method of the requests library

        :param path: Path of the API resource used in URL
        :param data: Data payload for POST request. JSON string
        :param params: Parameters for the request
        :return: Instance of ``requests`` response object
        """
        response = None
        args = {}
        if data:
            args["data"] = data
        if files:
            args["files"] = files
            del self.common_headers["headers"]["Content-type"]
        if params:
            args["params"] = params
        try:
            self.logger.debug(msg="_PUT: Path: '{}', Data: '{}', Params: '{}'".format(path, data, params))
            response = requests.put(url=self.path_base + path, **args, **self.common_headers)
        except ConnectionError:
            self.logger.critical(msg="_PUT: Could not connect to {}. Wrong address?".format(self.url))
        except Exception as e:
            self.logger.error(msg="_PUT: Encountered unhandled Exception: {}".format(repr(e)))
        finally:
            self.common_headers["headers"]["Content-type"] = "application/json"
            return response

    def _response_handler(self, response):
        """
        Function for handling request's response objects. Main purpose of this action is to handle HTTP return codes.
        In case of JSON formatted reply, returns this data as dictionary. In case of errors, either string representation
        of data is returned, or None. Status code is returned alongside the content to allow further processing if needed.

        :param response: Instance of request's response object.
        :return: content, status code
        """
        if response is None:
            return None, None
        try:
            status_code = response.status_code
            if status_code in range(200, 208):
                self.logger.debug(msg="Response_Handler: Server returned Status Code: {} OK".format(status_code))
                return response.json(), status_code
            if status_code == 400:
                self.logger.error(msg="Response_Handler: Server returned Status Code: {}, Bad Request.".format(status_code))
                try:
                    return response.json(), status_code
                except Exception as e:
                    self.logger.error(msg="Response_Handler: Could not return JSON error representation. Raw Text: {} Exception: {}.".format(response.text, status_code))
                    return response.text, status_code
            if status_code == 401:
                self.logger.error(msg="Response_Handler: Server returned Status Code: {}, Unauthorized.".format(status_code))
                return response.json(), status_code
            if status_code == 403:
                self.logger.error(msg="Response_Handler: Server returned Status Code: {}, Forbidden.".format(status_code))
                return response.text, status_code
            if status_code == 404:
                self.logger.error(msg="Response_Handler: Server returned Status Code: {}, Not Found.".format(status_code))
                return response.text, status_code
            if status_code in range(400, 500):
                self.logger.error(msg="Response_Handler: Server returned Status Code: {}, cannot process response.".format(status_code))
                return None, status_code
            if status_code in range(500, 600):
                self.logger.error(msg="Response_Handler: Server returned Status Code: {}, cannot process response.".format(status_code))
                return None, status_code
        except Exception as e:
            self.logger.critical(msg="Response Handler: Unhandled exception occurred. Exception: {}".format(repr(e)))

