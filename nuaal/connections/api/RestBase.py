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
        self.logger = get_logger(name="{}-{}".format(con_type if con_type else 'REST', self.url), DEBUG=DEBUG)
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
            self.logger.info(msg="No credentials provided, using cached instead.")
            if self._load_credentials():
                self.logger.info(msg="Credentials successfully loaded.")
            else:
                self.logger.info(msg="Failed to load valid credentials.")
        else:
            self._authorize()

    def _authorize(self):
        pass

    def _get(self, path, params=None):
        response = None
        try:
            self.logger.debug(msg="_GET: Path: '{}', Params: '{}'".format(path, params))
            if params:
                response = requests.get(url=self.path_base + path, **self.common_headers, params=params)
            else:
                response = requests.get(url=self.path_base + path, **self.common_headers)
        except ConnectionError:
            self.logger.critical(msg="_GET: Could not connect to {}. Wrong address?".format(self.url))
        except Exception as e:
            self.logger.error(msg="_GET: Encountered unhandled Exception: {}".format(repr(e)))
        finally:
            return response

    def _post(self, path, data, params=None):
        response = None
        try:
            self.logger.debug(msg="_POST: Path: '{}', Data: '{}', Params: '{}'".format(path, data, params))
            if params:
                response = requests.post(url=self.path_base + path, data=data, **self.common_headers, params=params)
            else:
                response = requests.post(url=self.path_base + path, data=data, **self.common_headers)
        except ConnectionError:
            self.logger.critical(msg="_POST: Could not connect to {}. Wrong address?".format(self.url))
        except Exception as e:
            self.logger.error(msg="_POST: Encountered unhandled Exception: {}".format(repr(e)))
        finally:
            return response

    def _delete(self, path, params):
        response = None
        try:
            self.logger.debug(msg="_DELETE: Path: '{}', Params: '{}'".format(path, params))
            if params:
                response = requests.delete(url=self.path_base + path, **self.common_headers, params=params)
            else:
                response = requests.delete(url=path, **self.common_headers)
        except ConnectionError:
            self.logger.critical(msg="_DELETE: Could not connect to {}. Wrong address?".format(self.url))
        except Exception as e:
            self.logger.error(msg="_DELETE: Encountered unhandled Exception: {}".format(repr(e)))
        finally:
            return response

    def _put(self, path, data, params):
        response = None
        try:
            self.logger.debug(msg="_PUT: Path: '{}', Data: '{}', Params: '{}'".format(path, data, params))
            if params:
                response = requests.put(url=self.path_base + path, data=data, **self.common_headers, params=params)
            else:
                response = requests.put(url=self.path_base + path, data=data, **self.common_headers)
        except ConnectionError:
            self.logger.critical(msg="_PUT: Could not connect to {}. Wrong address?".format(self.url))
        except Exception as e:
            self.logger.error(msg="_PUT: Encountered unhandled Exception: {}".format(repr(e)))
        finally:
            return response

    def _response_handler(self, response):
        if response is None:
            return None, None
        try:
            status_code = response.status_code
            if status_code in range(200, 208):
                self.logger.debug(msg="Response_Handler: Server returned Status Code: {} OK".format(status_code))
                return response.json(), status_code
            if status_code == 400:
                self.logger.error(msg="Response_Handler: Server returned Status Code: {}, Bad Request.".format(status_code))
                return None, status_code
            if status_code == 401:
                self.logger.error(msg="Response_Handler: Server returned Status Code: {status_code}, Unauthorized.".format(status_code))
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


