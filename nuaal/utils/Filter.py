from nuaal.utils import get_logger
import copy


class Filter:
    """
    Object for making filtering of required field easier.
    """
    def __init__(self, required={}, excluded={}, exact_match=True, DEBUG=False):
        """
        This class finds elements in JSON-like format based on provided values.

        :param dict required: Dictionary of required keys. Example: `{"key1": "value1"}` will return only those dictionaries, which key `"key1"` \
               contains the value `"value1"`. You can also use list of required values, such as `{"key1": ["value1", "value2"]}` together with option \
               ``exact_match=False``.

        :param dict excluded: Dictionary of excluded keys. Example: `{"key1": "value1"}` will return only those dictionaries, which key `"key1"` \
               does not contain the value `"value1"`. You can also use list of excluded values, such as `{"key1": ["value1", "value2"]}` together with option \
               ``exact_match=False``.

        :param bool exact_match: Specifies whether the filter value must match exactly, or partially.
        :param DEBUG: Enables/disables debugging output.
        """
        self.logger = get_logger(name="Filter", DEBUG=DEBUG)
        self.required = None
        self.excluded = None
        if isinstance(required, dict):
            self.required = required
        else:
            self.required = {}
            self.logger.error(msg="Required is not a dictionary!")
        if isinstance(excluded, dict):
            self.excluded = excluded
        else:
            self.excluded = {}
            self.logger.error(msg="Excluded is not a dictionary!")
        self.exact_match = exact_match

    def __str__(self):
        return "[FilterObject: Required='%s' Excluded='%s' Exact-match: %s]" % (str(self.required), str(self.excluded), str(self.exact_match))

    def dict_cleanup(self, data):
        """
        Function for filtering dictionary structures (eg. dictionary where values are also dictionaries).

        :param dict data: Dictionary containing dicts as values, which you want to filter.
        :return: Filtered dictionary.
        """
        for data_key, data_value in list(data.items()):
            # TODO: Add DEBUG logging (?)
            for filter_key, filter_value in self.required.items():
                if filter_key in data_value.keys():
                    if isinstance(filter_value, str) and self.exact_match:
                        if data_value[filter_key] != filter_value:
                            del data[data_key]
                            break
                    elif isinstance(filter_value, str) and (not self.exact_match):
                        if data_value[filter_key] is None:
                            del data[data_key]
                            break
                        if filter_value not in data_value[filter_key]:
                            del data[data_key]
                            break
                    elif isinstance(filter_value, list) and self.exact_match:
                        if data_value[filter_key] not in filter_value:
                            del data[data_key]
                            break
                    elif isinstance(filter_value, list) and (not self.exact_match):
                        if data_value[filter_key] is None:
                            del data[data_key]
                            break
                        found_match = False
                        for filter_value_item in filter_value:
                            if filter_value_item in data_value[filter_key]:
                                found_match = True
                        if not found_match:
                            del data[data_key]
                            break
                    else:
                        self.logger.warning(msg="Dict_Cleanup: None of the cases matched. Data: %s Filter: %s" % (data_value, self.filter))
                        # TODO: Handle other possible cases
                else:
                    self.logger.warning(msg="Dict_Cleanup: Filter key: %s not present in Data: %s" % (filter_key, data_value))
                    continue

        for data_key, data_value in list(data.items()):
            # TODO: Add DEBUG logging (?)
            for filter_key, filter_value in self.excluded.items():
                if filter_key in data_value.keys():
                    if isinstance(filter_value, str) and self.exact_match:
                        if data_value[filter_key] == filter_value:
                            del data[data_key]
                            break
                    elif isinstance(filter_value, str) and (not self.exact_match):
                        if data_value[filter_key] is None:
                            continue
                        if filter_value in data_value[filter_key]:
                            del data[data_key]
                            break
                    elif isinstance(filter_value, list) and self.exact_match:
                        if data_value[filter_key] in filter_value:
                            del data[data_key]
                            break
                    elif isinstance(filter_value, list) and (not self.exact_match):
                        if data_value[filter_key] is None:
                            continue
                        found_match = False
                        for filter_value_item in filter_value:
                            if filter_value_item in data_value[filter_key]:
                                found_match = True
                        if found_match:
                            del data[data_key]
                            break
                    else:
                        self.logger.warning(msg="Dict_Cleanup: None of the cases matched. Data: %s Filter: %s" % (data_value, self.filter))
                        # TODO: Handle other possible cases
                else:
                    self.logger.warning(msg="Dict_Cleanup: Filter key: %s not present in Data: %s" % (filter_key, data_value))
                    continue
        return data

    def list_cleanup(self, data):
        """
        Function for filtering list structures (eg. list of dictionaries).

        :param list data: List of dictionaries, which you want to filter.
        :return: Filtered list of dictionaries.
        """
        for data_value in list(data):
            # TODO: Add DEBUG logging (?)
            for filter_key, filter_value in self.required.items():
                if filter_key in data_value.keys():
                    if isinstance(filter_value, str) and self.exact_match:
                        if data_value[filter_key] != filter_value:
                            data.remove(data_value)
                            break
                    elif isinstance(filter_value, str) and (not self.exact_match):
                        if data_value[filter_key] is None:
                            data.remove(data_value)
                            break
                        if filter_value not in data_value[filter_key]:
                            data.remove(data_value)
                            break
                    elif isinstance(filter_value, list) and self.exact_match:
                        if data_value[filter_key] not in filter_value:
                            data.remove(data_value)
                            break
                    elif isinstance(filter_value, list) and (not self.exact_match):
                        if data_value[filter_key] is None:
                            data.remove(data_value)
                            break
                        found_match = False
                        for filter_value_item in filter_value:
                            if filter_value_item in data_value[filter_key]:
                                found_match = True
                        if not found_match:
                            data.remove(data_value)
                            break
                    else:
                        self.logger.warning(msg="List_Cleanup: None of the cases matched. Data: %s Filter: %s" % (data_value, self.filter))
                        # TODO: Handle other possible cases
                else:
                    self.logger.warning(msg="List_Cleanup: Filter key: %s not present in Data: %s" % (filter_key, data_value))
                    continue

        for data_value in list(data):
            # TODO: Add DEBUG logging (?)
            for filter_key, filter_value in self.excluded.items():
                if filter_key in data_value.keys():
                    if isinstance(filter_value, str) and self.exact_match:
                        if data_value[filter_key] == filter_value:
                            data.remove(data_value)
                            break
                    elif isinstance(filter_value, str) and (not self.exact_match):
                        if data_value[filter_key] is None:
                            continue
                        if filter_value in data_value[filter_key]:
                            data.remove(data_value)
                            break
                    elif isinstance(filter_value, list) and self.exact_match:
                        if data_value[filter_key] in filter_value:
                            data.remove(data_value)
                            break
                    elif isinstance(filter_value, list) and (not self.exact_match):
                        if data_value[filter_key] is None:
                            continue
                        found_match = False
                        for filter_value_item in filter_value:
                            if filter_value_item in data_value[filter_key]:
                                found_match = True
                        if found_match:
                            data.remove(data_value)
                            break
                    else:
                        self.logger.warning(msg="List_Cleanup: None of the cases matched. Data: %s Filter: %s" % (data_value, self.filter))
                        # TODO: Handle other possible cases
                else:
                    self.logger.warning(msg="List_Cleanup: Filter key: %s not present in Data: %s" % (filter_key, data_value))
                    continue

        return data

    def universal_cleanup(self, data=None):
        """
        This function calls proper cleanup function base on data type.

        :param data: Data to be filtered, either list of dictionaries or dictionary of dictionaries.
        :return: Filtered data
        """
        data = copy.deepcopy(data)
        output = None
        if isinstance(data, list):
            output = self.list_cleanup(data=data)
        elif isinstance(data, dict):
            output = self.dict_cleanup(data=data)
        else:
            self.logger.error(msg="Universal_Cleanup: Given data is neither list nor dict.")
        return output

class OutputFilter:
    """
    This class helps to minimize dictionary structure by specifying only the desired keys.
    """
    def __init__(self, data=None, required=[], excluded=[]):
        """

        :param data: Data to be filtered.
        :param list required: List of required keys. Returned entries will contain only these specified keys. Example: `{"key1": "value1", "key2": "value2"}` \
               with ``required`` `["key1"]` will only return `{"key1": "value1"}`.

        :param list excluded: List of excluded keys. Returned entries will not contain these specified keys. Example: `{"key1": "value1", "key2": "value2"}` \
               with ``excluded`` `["key1"]` will only return `{"key2": "value2"}`.
        """
        self.logger = get_logger(name="OutputFilter")
        self.data = copy.deepcopy(data)
        self.required = None
        self.excluded = None
        if isinstance(required, list):
            self.required = required
        else:
            self.required = []
            self.logger.error(msg="Required is not a list!")
        if isinstance(excluded, list):
            self.excluded = excluded
        else:
            self.excluded = []
            self.logger.error(msg="Excluded is not a list!")

    def get(self):
        """
        After instantiating object, call this function to retrieve filtered data.

        :return: Filtered data.
        """
        if isinstance(self.data, dict):
            for id, data in list(self.data.items()):
                if len(self.required) > 0:
                    # Loop over required keys
                    for key in list(data.keys()):
                        if key not in self.required:
                            del self.data[id][key]
                elif len(self.excluded) > 0:
                    # Loop over excluded keys
                    for key in list(data.keys()):
                        if key in self.excluded:
                            del self.data[id][key]
                else:
                    continue
            return self.data

        elif isinstance(self.data, list):
            for i in range(len(self.data)):
                if isinstance(self.data[i], dict):
                    if len(self.required) > 0:
                        for key in list(self.data[i].keys()):
                            if key not in self.required:
                                del self.data[i][key]
                    elif len(self.blocked) > 0:
                        for key in list(self.data[i].keys()):
                            if key in self.excluded:
                                del self.data[i][key]
                    else:
                        continue
            return self.data

        else:
            self.logger.error(msg="Data is not a dict or list!")
            return None