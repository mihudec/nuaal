import os
import sys
import json
from nuaal.utils import get_logger, check_path
from nuaal.definitions import ROOT_DIR, DATA_PATH



class Writer:
    def __init__(self, type, DEBUG=False):
        self.type = type
        self.logger = get_logger(name="{}-Writer".format(self.type), DEBUG=DEBUG)

    def __str__(self):
        return "[{}-Writer]".format(self.type)

    def __repr__(self):
        return "[{}-Writer]".format(self.type)

    def json_to_lists(self, data):
        headers = []
        list_data = []
        if isinstance(data, list) and len(data) > 0:
            if isinstance(data[0], dict):
                headers = list(data[0].keys())
                self.logger.debug(msg="Successfully created headers: {}".format(headers))
                for entry in data:
                    entry_list = []
                    for element in [entry[x] for x in headers]:
                        if isinstance(element, list):
                            entry_list.append(str(element))
                        else:
                            entry_list.append(element)
                    list_data.append(entry_list)
                return {"headers": headers, "list_data": list_data}

    def _get_headers(self, data):
        if isinstance(data, dict):
            headers = list(data.keys())
            headers.sort()
            return headers
        elif isinstance(data, list):
            headers = set()
            for entry in data:
                if isinstance(entry, dict):
                    for key in entry.keys():
                        headers.add(key)
            headers = list(headers)
            headers.sort()
            return headers

    def combine_data(self, data):
        sections = set()
        section_headers = {}
        section_content = {}
        common_headers = ["hostname", "ipAddress"]
        if isinstance(data, list):
            # Create sections and sections headers
            for device in data:
                print(device["hostname"], device["ipAddress"])
                for section in device.keys():
                    if section not in common_headers:
                        section_content[section] = []
                        sections.add(section)
                        if isinstance(device[section], list):
                            section_headers[section] = common_headers + list(device[section][0].keys())
                            for entry in device[section]:
                                section_content[section].append([device[x] for x in common_headers] + [entry[x] for x in section_headers[section][len(common_headers):]])
            #print(sections)
            #print(section_headers)
            #print(json.dumps(section_content, indent=1))
            return section_headers, section_content

        elif isinstance(data, str):
            self.logger.warning(msg="Given data is a string. List of dictionaries is preferred.")
            try:
                data = json.loads(data)
                return self.json_to_lists(data=data)
            except:
                self.logger.critical(msg="Given data is not a valid JSON string.")
                return None

        pass


    def combine_device_data(self, data):
        # This function might be overly complicated for its purpose
        # Currently it tries to handle not consistent data, where different devices might have
        # different section and dictionary keys...
        common_headers = ["hostname", "ipAddress"]
        sections = set()
        section_headers = {}
        section_data = {}
        if isinstance(data, list):
            for device in data:
                for section in device.keys():
                    if section not in common_headers:
                        sections.add(section)
            sections = list(sections)
            sections.sort()
            for section in sections:
                section_headers[section] = []
                section_data[section] = []
            for device in data:
                for section in sections:
                    try:
                        #print(device[section])
                        #print(self._get_headers(device[section]))
                        for header in self._get_headers(device[section]):
                            if header not in section_headers[section]:
                                section_headers[section].append(header)
                    except Exception as e:
                        self.logger.error(msg="Combine Device Data raised an Exception: {}. Maybe inconsistent data?".format(repr(e)))
            for section in section_headers.keys():
                section_headers[section] = common_headers + section_headers[section]
        else:
            self.logger.critical(msg="Given data is not a list of dictionaries.")
        for device in data:
            for section in sections:
                #print(section_headers[section])
                for entry in device[section]:
                    temp = []
                    for header in section_headers[section][:len(common_headers)]:
                        temp.append(device[header])
                    for header in section_headers[section][len(common_headers):]:
                        try:
                            temp.append(entry[header])
                        except Exception as e:
                            self.logger.warning(msg="Exception raised: {}, maybe missing key?".format(repr(e)))
                            temp.append(None)
                    section_data[section].append(temp)
        return section_headers, section_data


