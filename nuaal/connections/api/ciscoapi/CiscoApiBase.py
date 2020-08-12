from nuaal.connections.api import RestBase
from nuaal.definitions import DATA_PATH, TIMESTAMP_FORMAT
import requests
import json
from urllib.parse import quote
from threading import Thread
from queue import Queue
from datetime import datetime


class CiscoApiBase(RestBase):

    def __init__(self, url="https://api.cisco.com", username=None, password=None, api_user_id="default", api_base_path="", verify_ssl=False, con_type=None, DEBUG=False):
        super(CiscoApiBase, self).__init__(url=url,
                                           username=username,
                                           password=password,
                                           api_base_path=api_base_path,
                                           verify_ssl=verify_ssl,
                                           con_type=con_type if con_type else "CiscoAPI",
                                           DEBUG=DEBUG
                                           )
        self.headers["Accept"] = "application/json"
        self.api_user_id = api_user_id
        self.access_token = None
        self.token_type = None
        self.timestamp = None

    def _update_headers(self):
        self.headers["Authorization"] = "{} {}".format(self.token_type, self.access_token)
        self.headers["Accept"] = "application/json"
        self.common_headers = {"headers": self.headers, "verify": self.verify_ssl}

    def _load_credentials(self):

        with open(file="{}/csapi_credentials.json".format(DATA_PATH), mode="r") as f:
            credentials = json.load(fp=f)[self.api_user_id]
            for value in credentials.values():
                if value == "":
                    return False
            self.username = credentials["username"]
            self.password = credentials["password"]
            self.access_token = credentials["access_token"]
            self.token_type = credentials["token_type"]
            self.timestamp = datetime.strptime(credentials["timestamp"], TIMESTAMP_FORMAT)
            try:
                timestamp = datetime.strptime(credentials["timestamp"], TIMESTAMP_FORMAT)
                if (datetime.now()-timestamp).total_seconds() >= 3599:
                    self.logger.debug(msg="The loaded token has expired, getting new token...")
                    self._authorize()
                else:
                    self.logger.debug(msg="The loaded token should still be valid.")
            except Exception as e:
                self.logger.error(msg="Could not verify token based on timestamp. Exception: {}".format(repr(e)))
            self._update_headers()
            self.authorized = True
            self.logger.debug(msg="Successfully loaded credentials for api_user_id='{}'".format(self.api_user_id))
            return True

    def _store_credentials(self):
        self.logger.info(msg="Storing credentials.")
        credentials = {}
        try:
            with open(file="{}/csapi_credentials.json".format(DATA_PATH), mode="r") as f:
                credentials = json.load(f)
            credentials[self.api_user_id] = {"username": self.username, "password": self.password, "access_token": self.access_token, "token_type": self.token_type, "timestamp": datetime.strftime(datetime.now(), TIMESTAMP_FORMAT)}
            with open(file="{}/csapi_credentials.json".format(DATA_PATH), mode="w") as f:
                json.dump(obj=credentials, fp=f, indent=2)
            self.logger.debug(msg="Successfully updated stored credentials for api_user_id='{}'".format(self.api_user_id))

        except FileNotFoundError:
            with open(file="{}/csapi_credentials.json".format(DATA_PATH), mode="w") as f:
                json.dump(obj={self.api_user_id: {"username": self.username, "password": self.password, "access_token": self.access_token, "token_type": self.token_type, "timestamp": datetime.strftime(datetime.now(), TIMESTAMP_FORMAT)}}, fp=f, indent=2)
                self.logger.debug(msg="Successfully stored credentials for api_user_id='{}'".format(self.api_user_id))
        except Exception as e:
            self.logger.critical(msg="Could not store credentials. Exception: '{}'".format(repr(e)))

    def _authorize(self):

        auth_url = "https://cloudsso.cisco.com/as/token.oauth2"
        payload = "client_id={}&client_secret={}&grant_type=client_credentials".format(self.username, self.password)
        response = requests.post(url=auth_url, data=payload, headers={'Content-Type': 'application/x-www-form-urlencoded', 'Accept': 'application/json'}, verify=self.verify_ssl)
        status_code = response.status_code
        if status_code == 200:
            response = response.json()
            print(response)
            self.access_token = response["access_token"]
            self.token_type = response["token_type"]
            self.timestamp = datetime.strftime(datetime.now(), TIMESTAMP_FORMAT)
            self.logger.debug(msg="Successfully obtained access token: '{}'".format(self.access_token))
            self._update_headers()
            self._store_credentials()
            self.authorized = True
        elif status_code == 401:
            try:
                if response.json()["error_description"] == "Invalid client or client credentials":
                    self.logger.critical(msg="Could not get Access Token. Reason: Invalid Credentials. Please provide valid credentials.")
                    self.authorized = False
            except Exception as e:
                self.logger.error(msg="_Authorize: Unhandled Exception occurred. Exception: {}".format(repr(e)))
                self.authorized = False
        else:
            print(status_code)
            print(response.json())

    def get(self, path, params=None):
        """
        Function providing HTTP GET method for retrieving data from APIC-EM API.

        :param path: Path of API resource, such as "/network-device". Each path must begin with "/" forward-slash character
        :param params: Dictionary of parameters for request, such as {"deviceId": "<ID of device in APIC-EM database>"}
        :return: Dictionary representation of response content under "response" key, eg. <request_response_object>show_ip_route.json()["response"] or ``None``
        """
        if not self.authorized:
            self.logger.error(msg="Connection is not authorized")
            return None
        response, status_code = self._response_handler(self._get(path=path, params=params))
        if status_code in range(200, 208):
            #print(response)
            return response
        elif status_code == 401 or status_code == 403:
            self.authorized = False
            self._authorize()
            return self.get(path=path, params=params)
        else:
            self.logger.error(msg="GET: Could not retrieve valid response for path '{}'. Response: {}".format(path, response))
            return None

    def worker_get(self, path, params, in_queue, outputs):
        while not in_queue.empty():
            chunk = in_queue.get()
            query = ",".join(chunk)
            response = self.get(path="/{}/{}".format(path, query))
            outputs.append(response)
            in_queue.task_done()


    def get_threaded(self, path, queries, max_query_len, workers, params=None):
        if isinstance(queries, str):
            queries = queries.split(",")
        # Make sure queries don't contain trailing spaces
        queries = [x.strip() for x in queries]
        # Split queries by max_query_length
        chunks = [queries[x:x + max_query_len] for x in range(0, len(queries), max_query_len)]
        if len(chunks) < workers:
            workers = len(chunks)
        in_queue = Queue()
        for chunk in chunks:
            in_queue.put(chunk)
        threads = []
        outputs = []
        for i in range(workers):
            t = Thread(name="QueryThread-{}".format(i), target=self.worker_get, args=(path, params, in_queue, outputs))
            threads.append(t)
        [t.start() for t in threads]
        in_queue.join()
        return outputs


if __name__ == '__main__':
    # client = CiscoApiBase(url="https://api.cisco.com", api_user_id="an", api_base_path="/supporttools/eox/rest/5", DEBUG=True)
    # client._initialize()
    # client.get_threaded(path="/EOXByProductID", max_query_len=20, workers=10, queries=["WS-C3850-24T-L","WS-C3850-48T-L","WS-C3850-24P-L","WS-C3850-24U-L","WS-C3850-48P-L","WS-C3850-48F-L","WS-C3850-48U-L","WS-C3850-24T-S","WS-C3850-48T-S","WS-C3850-24P-S","WS-C3850-24U-S","WS-C3850-48P-S","WS-C3850-48F-S","WS-C3850-48U-S","WS-C3850-24T-E","WS-C3850-48T-E","WS-C3850-24P-E","WS-C3850-24U-E","WS-C3850-48P-E","WS-C3850-48F-E","WS-C3850-48U-E","WS-C3850-12X48U-L","WS-C3850-12X48U-S","WS-C3850-12X48U-E","WS-C3850-24XU-L","WS-C3850-24XU-S","WS-C3850-24XU-E","WS-C3850-12S-S","WS-C3850-12S-E","WS-C3850-24S-S","WS-C3850-24S-E","WS-C3850-12XS-S","WS-C3850-12XS-E","WS-C3850-24XS-S","WS-C3850-24XS-E","WS-C3850-48XS-S","WS-C3850-48XS-E","WS-C3850-48XS-F-S","WS-C3850-48XS-F-E","WS-C3850-24PW-S","WS-C3850-48PW-S","WS-C3850-24UW-S","WS-C3850-48W-S ","WS-C3850-48UW-S","WS-C3850-24XUW-S","WS-C3850-12X48UW-S","WS-C3850-16XS-S","WS-C3850-16XS-E","WS-C3850-32XS-S","WS-C3850-32XS-E"])


    serials = ['FOC2145T0A6', 'FCW1816B142', 'FOC1817S4Y2', 'FCW1821A353', 'FCW1821A2R2', 'FCW2143A3HR', 'FCW1821A37K', 'FCW2046B09R', 'FCW1826B1BS', 'FCW2122B1XB', 'FOC2220V0DL', 'FOC1948S42F', 'FOC2220S0KN', 'FOC1948S42A', 'FCW2122B1YL', 'FOC2001S381', 'FOC1821S2ZM', 'FCW2143B4DZ', 'FCW2143B4DD', 'FOC2138T3A1', 'FCW2116B658', 'FCW2143B4DU', 'FOC2001S0X8', 'FCW1952A13C', 'FCW2217B2A7', 'FOC2219S251', 'FOC1818S07Z', 'FCW1818B0H0', 'FCW1821A2QQ', 'FCW1816B163', 'FCW2046B09P', 'FCW2046B09N', 'FOC2145T0BU', 'FCW2143A3HZ', 'FCW2109B1D9', 'FCW2122B1WC', 'FCW2122B1X6', 'FCW1821A2X4', 'FCW1821A350', 'FCW1821A2WZ', 'FCW1821A2TN', 'FCW1821A2X3', 'FCW1816B11H', 'FCW1816B10D', 'FCW1816B161', 'FCW1816B0YD', 'FCW2009B2EK']

    api = CiscoApiBase(url="https://api.cisco.com", api_user_id="an", api_base_path="/sn2info/v2/coverage/summary", DEBUG=True)
    api._initialize()
    result = api.get_threaded(path="serial_numbers", queries=serials, max_query_len=10, workers=10)
    print(result)
    result = [x["serial_numbers"] for x in result]
    result =