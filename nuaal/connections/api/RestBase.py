import timeit
import logging
import requests
from requests.auth import HTTPBasicAuth
from requests.exceptions import ConnectionError, Timeout
import json
from nuaal.definitions import DATA_PATH
from nuaal.utils import get_logger

class RestBase(object):
    def __init__(self, url, username=None, password=None, api_base_path=None, verify_ssl=False, DEBUG=False, con_type=None):
        # Disable logging for external libraries
        logging.getLogger("requests").setLevel(logging.WARNING)
        logging.getLogger("urllib3").setLevel(logging.WARNING)

        self.url = url
        self.logger = get_logger(name=f"{con_type if con_type else 'REST'}-{self.url}", DEBUG=DEBUG)
        self.username = username
        self.password = password
        self.api_base_path = api_base_path
        self.verify_ssl = verify_ssl
        self.DEBUG = DEBUG
        self.path_base = self.url + self.api_base_path
        self.headers = {"Content-type": "application/json"}
        self.common_headers = {"headers": self.headers, "verify": self.verify_ssl}

    def _initialize(self):
        if self.verify_ssl == False:
            # Disable certificate warning
            try:
                requests.packages.urllib3.disable_warnings()
            except:
                self.logger.warning(msg="Failed to disable Certificate Warnings")
        if self.username is None or self.password is None:
            self.logger.info(msg=f"No credentials provided, using cached instead.")
            if self._load_credentials():
                self.logger.info(msg=f"Credentials successfully loaded.")
            else:
                self.logger.info(msg=f"Failed to load valid credentials.")
        else:
            self._authorize()

    def _authorize(self):
        pass

    def _get(self, path, params=None):
        response = None
        try:
            self.logger.debug(msg=f"_GET: Path: '{path}', Params: '{params}'")
            if params:
                response = requests.get(url=self.path_base + path, **self.common_headers, params=params)
            else:
                response = requests.get(url=self.path_base + path, **self.common_headers)
        except ConnectionError:
            self.logger.critical(msg=f"_GET: Could not connect to {self.url}. Wrong address?")
        except Exception as e:
            self.logger.error(msg=f"_GET: Encountered unhandled Exception: {repr(e)}")
        finally:
            return response

    def _post(self, path, data, params=None):
        response = None
        try:
            self.logger.debug(msg=f"_POST: Path: '{path}', Data: '{data}', Params: '{params}'")
            if params:
                response = requests.post(url=self.path_base + path, data=data, **self.common_headers, params=params)
            else:
                response = requests.post(url=self.path_base + path, data=data, **self.common_headers)
        except ConnectionError:
            self.logger.critical(msg=f"_POST: Could not connect to {self.url}. Wrong address?")
        except Exception as e:
            self.logger.error(msg=f"_POST: Encountered unhandled Exception: {repr(e)}")
        finally:
            return response

    def _delete(self, path, params):
        response = None
        try:
            self.logger.debug(msg=f"_DELETE: Path: '{path}', Data: '{data}', Params: '{params}'")
            if params:
                response = requests.delete(url=self.path_base + path, **self.common_headers, params=params)
            else:
                response = requests.delete(url=path, **self.common_headers)
        except ConnectionError:
            self.logger.critical(msg=f"_DELETE: Could not connect to {self.url}. Wrong address?")
        except Exception as e:
            self.logger.error(msg=f"_DELETE: Encountered unhandled Exception: {repr(e)}")
        finally:
            return response

    def _put(self, path, data, params):
        response = None
        try:
            self.logger.debug(msg=f"_PUT: Path: '{path}', Data: '{data}', Params: '{params}'")
            if params:
                response = requests.put(url=self.path_base + path, data=data, **self.common_headers, params=params)
            else:
                response = requests.put(url=self.path_base + path, data=data, **self.common_headers)
        except ConnectionError:
            self.logger.critical(msg=f"_PUT: Could not connect to {self.url}. Wrong address?")
        except Exception as e:
            self.logger.error(msg=f"_PUT: Encountered unhandled Exception: {repr(e)}")
        finally:
            return response

    def _response_handler(self, response):
        if response is None:
            return None, None
        try:
            status_code = response.status_code
            if status_code in range(200, 208):
                self.logger.debug(msg=f"Response_Handler: Server returned Status Code: {status_code} OK")
                return response.json(), status_code
            if status_code == 400:
                self.logger.error(msg=f"Response_Handler: Server returned Status Code: {status_code}, Bad Request.")
                return None, status_code
            if status_code == 401:
                self.logger.error(msg=f"Response_Handler: Server returned Status Code: {status_code}, Unauthorized.")
                return response.json(), status_code
            if status_code == 403:
                self.logger.error(msg=f"Response_Handler: Server returned Status Code: {status_code}, Forbidden.")
                return response.text, status_code
            if status_code == 404:
                self.logger.error(msg=f"Response_Handler: Server returned Status Code: {status_code}, Not Found.")
                return response.text, status_code
            if status_code in range(400, 500):
                self.logger.error(msg=f"Response_Handler: Server returned Status Code: {status_code}, cannot process response.")
                return None, status_code
            if status_code in range(500, 600):
                self.logger.error(msg=f"Response_Handler: Server returned Status Code: {status_code}, cannot process response.")
                return None, status_code
        except Exception as e:
            self.logger.critical(msg=f"Response Handler: Unhandled exception occurred. Exception: {repr(e)}")


