from nuaal.connections.api import RestBase
from nuaal.definitions import DATA_PATH
from nuaal.utils import check_path
import json
import os
import copy
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
        self._initialize()

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
                self.authorized = False

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
        :return: Dictionary representation of response content under "response" key, eg. <request_response_object>show_ip_route.json()["response"] or ``None``
        """
        if not self.authorized:
            self.logger.error(msg="Connection is not authorized")
            return None
        response, status_code = self._response_handler(self._get(path=path, params=params))
        if status_code in range(200, 208):
            #print(response)
            return response["response"]
        elif status_code == 401:
            self.authorized = False
            self._authorize()
            return self.get(path=path, params=params)
        else:
            self.logger.error(msg="GET: Could not retrieve valid response for path '{}'. Response: {}".format(path, response))
            return None

    def post(self, path, data=None, files=None, params=None):
        """
        Function providing HTTP POST method for sending data to APIC-EM API.

        :param str path: Path of API resource, such as "/ticket". Each path must begin with "/" forward-slash character
        :param json data: JSON string data payload
        :param dict files: Dictionary with files to upload
        :param params: Dictionary of parameters for request, such as {"deviceId": "<ID of device in APIC-EM database>"}
        :return: Dictionary representation of response content under "response" key, eg. <request_response_object>show_ip_route.json()["response"] or ``None``
        """
        if not self.authorized:
            return None
        response, status_code = self._response_handler(self._post(path=path, data=data, files=files, params=params))
        if status_code in range(200, 208):
            return response["response"]
        elif status_code == 401:
            self.authorized = False
            self._authorize()
            return self.post(path=path, data=data, files=files, params=params)
        else:
            self.logger.error(msg="GET: Could not retrieve valid response for path '{}', Response: {}".format(path, response))
            return None

    def put(self, path, data=None, files=None, params=None):
        """
        Function providing HTTP PUT method for sending data to APIC-EM API.

        :param str path: Path of API resource
        :param json data: JSON string data payload
        :param dict files: Dictionary with files to upload
        :param dict params: Dictionary of parameters for request, such as {"deviceId": "<ID of device in APIC-EM database>"}
        :return: Dictionary representation of response content under "response" key, eg. <request_response_object>show_ip_route.json()["response"] or ``None``
        """
        if not self.authorized:
            return None
        response, status_code = self._response_handler(self._put(path=path, data=data, files=files, params=params))
        if status_code in range(200, 208):
            return response["response"]
        elif status_code == 401:
            self.authorized = False
            self._authorize()
            return self.put(path=path, data=data, files=files, params=params)
        else:
            self.logger.error(msg="PUT: Could not retrieve valid response for path '{}'".format(path))
            return None

    def delete(self, path, params=None):
        """

        :param str path: Path of API resource
        :param dict params: Dictionary of parameters for request
        :return: Dictionary representation of response
        """
        if not self.authorized:
            return None
        response, status_code = self._response_handler(self._delete(path=path, params=params))
        if status_code in range(200, 208):
            return response["response"]
        elif status_code == 401:
            self.authorized = False
            self._authorize()
            return self.delete(path=path, params=params)
        else:
            self.logger.error(msg="DELETE: Could not retrieve valid response for path '{}'".format(path))
            return None

    def check_file(self, fileId=None, namespace=None, file_name=None):
        """
        Function for checking whether given file (based on it's name or ID) exists on the APIC-EM. Can be used for checking configuration or template files.

        :param str fileId: ID string of the file in APIC-EM's database
        :param str namespace: APIC-EM's namespace, under which the file should be located
        :param str file_name: Name of the file
        :return str: FileID
        """
        if fileId:
            response = self._get(path="/file/{}".format(fileId))
            status_code = response.status_code
            response = response.text
            if status_code == 200:
                self.logger.debug(msg="File with ID: '{}' exists.".format(fileId))
                return fileId
        else:
            file_id = None
            namespaces = self.get(path="/file/namespace")
            if namespace in namespaces:
                self.logger.debug(msg="File namespace {} exists.".format(namespace))
                files = self.get(path="/file/namespace/{}".format(namespace))
                for file in files:
                    try:
                        if file["name"] == file_name:
                            file_id = file["id"]
                            self.logger.info(msg="File with name {} already exists on APIC-EM with ID: '{}'".format(file_name, file_id))
                            break
                    except Exception as e:
                        self.logger.error(msg="Check File encountered unhandled Exception: {}".format(repr(e)))
                if file_id is None:
                    self.logger.info(msg="File '{}' does not exists on APIC-EM under namespace {}.".format(file_name, namespace))
                return file_id
            else:
                self.logger.info(msg="Namespace '{}' does not exists.".format(namespace))
                return file_id

    def delete_file(self, fileId=None, namespace=None, filename=None):
        """
        Function for deleting file from APIC-EM's database based on it's ID

        :param str fileId: ID string of the file in APIC-EM's database
        :param str namespace: APIC-EM's namespace, under which the file should be located
        :param str filename: Name of the file
        :return bool:
        """
        if fileId:
            response = self.get(path="/file/{}".format(fileId))
            if response:
                self.logger.debug()
            response = self.delete(path="/file/{}".format(fileId))
            if response == "File id={} is deleted successfully".format(fileId):
                return True
            else:
                return False


    def upload_file(self, namespace, file_path):
        """
        Function for uploading file to APIC-EM's database.

        :param str namespace: APIC-EM's namespace, under which the file should be uploaded
        :param str file_path: Path to the file on local machine
        :return str: FileID of the uploaded file
        """
        file_name = os.path.basename(file_path)
        file_path = check_path(os.path.dirname(file_path), create_missing=False)
        if file_path:
            file_path = os.path.abspath(os.path.join(file_path, file_name))
            if os.path.isfile(file_path):
                file_name = os.path.basename(file_path)
            else:
                self.logger.error(msg="Given file_path is not a valid path to file.")
                return None
        else:
            self.logger.error(msg="Given file_path does not exist.")
            return None
        file_id = self.check_file(namespace=namespace, file_name=file_name)
        if file_id:
            self.logger.info(msg="File '{}' in namespace '{}' already exists with ID: '{}'".format(file_name, namespace, file_id))
            return file_id
        else:
            file_path = file_path
            file = None
            if file_path:
                try:
                    file = open(file_path, mode="rb")
                    self.logger.debug(msg="Upload file: File '{}' successfully opened.".format(file_name))
                except Exception as e:
                    self.logger.error(msg="Could not open file '{}' for reading.".format(file_name))
                    return file_id
                try:
                    response = self.post(path="/file/{}".format(namespace), files={file_name: file})
                    file_id = response["id"]
                except Exception as e:
                    self.logger.error(msg="Could not upload file '{}' to namespace {}. Exception: {}".format(file_name, namespace, repr(e)))
                finally:
                    return file_id


    def task_handler(self, taskId, timeout=2, max_retries=2):
        """
        Function for handling Task results, based on taskId.
        This function periodically queries APIC-EM for the results of given task until task is either completed or timeout is reached.
        Maximum time this function waits for result is (timeout * max_retries) seconds.

        :param str taskId: ID of the task, returned by the APIC-EM after starting task.
        :param int timeout: Number of seconds to wait after each unsuccessful request
        :param int max_retries: Maximum number of requests.
        :return str: ID of the result
        """
        progress = None
        result = None
        run_count = 0

        while run_count < max_retries:
            response = self.get(path="/task/{}".format(taskId))
            print(response)
            if response is not None:
                if response["isError"]:
                    self.logger.error(msg="Task Handler: Task '{0}' failed. Progress: '{1}' failureReason: '{2}'.".format(
                        taskId,
                        response["progress"],
                        response["failureReason"]
                    )
                    )
                    return None
                progress = str(response["progress"])
                self.logger.info(msg="Task Handler : Run:{0}: Progress is: '{1}'".format(run_count, progress))
                search_result = re.search(pattern=r"^(?P<id>([A-Za-z0-9]{8}-[A-Za-z0-9]{4}-[A-Za-z0-9]{4}-[A-Za-z0-9]{4}-[A-Za-z0-9]{12}))$", flags=re.MULTILINE, string=progress)
                if search_result:
                    self.logger.debug(msg="Task Handler : Run:{0} : Found ResultID: '{1}'".format(run_count, search_result.group("id")))
                    return search_result.group("id")
                else:
                    run_count += 1
                    time.sleep(timeout)
            else:
                self.logger.error(msg="Task Handler: Failed to get response for TaskID: '{}'".format(taskId))
                return None
        self.logger.error(msg="Task Handler: Failed to get ResultID for TaskID: '{0}'. Reason: Timeout.".format(taskId))
        return None

