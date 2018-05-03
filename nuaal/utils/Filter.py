from nuaal.utils import get_logger


class Filter:
    """
    Object for making filtering of required field easier
    """
    def __init__(self, required={}, excluded={}, exact_match=True, DEBUG=False):
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
        output = None
        if isinstance(data, list):
            output = self.list_cleanup(data=data)
        elif isinstance(data, dict):
            output = self.dict_cleanup(data=data)
        else:
            self.logger.error(msg="Universal_Cleanup: Given data is neither list nor dict.")
        return output