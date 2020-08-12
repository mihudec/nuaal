import logging
import sys
import os
import re
import collections
import pathlib
import json
from nuaal.definitions import LOG_PATH, ROOT_DIR, OUTPUT_PATH


def get_logger(name, DEBUG=False, verbosity=4, handle=["stderr"], with_threads=False):
    """
    This function provides common logging facility by creating instances of `loggers` from python standard ``logging`` library.

    :param str name: Name of the logger
    :param bool DEBUG: Enables/disables debugging output
    :param list handle: Changing value of this parameter is not recommended.
    :return: Instance of logger object
    """
    verbosity_map = {
        1: logging.CRITICAL,
        2: logging.ERROR,
        3: logging.WARNING,
        4: logging.INFO,
        5: logging.DEBUG
    }
    if DEBUG:
        verbosity = 5

    threading_formatter_string = '[%(asctime)s] [%(levelname)s]\t[%(name)s][%(threadName)s][%(module)s][%(funcName)s]\t%(message)s'
    single_formatter_string = '[%(asctime)s] [%(levelname)s]\t[%(name)s][%(module)s][%(funcName)s]\t%(message)s'

    formatter_string = threading_formatter_string if with_threads else single_formatter_string

    logfile_path = os.path.join(check_path(LOG_PATH), "log.txt")
    formatter = logging.Formatter(formatter_string)
    stdout_handler = logging.StreamHandler(sys.stdout)
    stderr_handler = logging.StreamHandler(sys.stderr)
    file_handler = logging.FileHandler(logfile_path)
    file_handler.setFormatter(formatter)
    file_handler.setLevel(logging.DEBUG)

    handlers = []
    if "stderr" in handle:
        handlers.append(stderr_handler)
    if "stdout" in handle:
        handlers.append(stdout_handler)


    for handler in handlers:
        handler.setFormatter(formatter)
        try:
            handler.setLevel(verbosity_map[verbosity])
        except KeyError:
            handler.setLevel(logging.INFO)

    root = logging.getLogger(name)
    root.propagate = 0
    root.setLevel(logging.DEBUG)
    if verbosity == 0:
        root.disabled = True
    has_handler = {"file_handler": False, "stderr_handler": False, "stdout_handler": False}
    for handler in root.handlers:
        if isinstance(handler, logging.FileHandler):
            has_handler["file_handler"] = True
        if isinstance(handler, logging.StreamHandler):
            has_handler["stderr_handler"] = True
    if not has_handler["file_handler"]:
        root.addHandler(file_handler)
    if not has_handler["stderr_handler"]:
        root.addHandler(stderr_handler)

    return root

def interface_split(interface):
    """
    Function for splitting names of interfaces to interface type and number. Example: `FastEthernet0/18` -> `FastEthernet`, `0/18`
    :param str interface: Interface name.
    :return: Interface type, interface number
    """
    int_type, int_num = None, None
    if isinstance(interface, str):
        search_result = re.search(r"(?P<int_type>\D+)(?P<int_num>\d.*)", interface)
        try:
            int_type = search_result.group("int_type")
            int_num = search_result.group("int_num")
        except:
            pass
        finally:
            return int_type, int_num

    else:
        search_result = re.search(r"interface\s(?P<int_type>\D+)(?P<int_num>\d.*)", interface.text)
        try:
            int_type = search_result.group("int_type")
            int_num = search_result.group("int_num")
        except:
            pass
        finally:
            return int_type, int_num


def vlan_range_expander(all_vlans):
    """
    Function for expanding list of allowed VLANs on trunk interface. Example: `1-4096` -> range(1, 4097). Can be used when trying to figure out whether certain
    VLAN is allowed or not. Reverse function is ``vlan_range_shortener``.

    :param all_vlans: Either list (`["1-10", "15", "20-30"]`) or string (`"1-10,15,20-30"`) of VLAN range.
    :return: List of VLAN numbers (integers).
    """
    if isinstance(all_vlans, list):
        pass
    elif isinstance(all_vlans, str):
        all_vlans = all_vlans.split(",")
    elif isinstance(all_vlans, int):
        all_vlans = [str(all_vlans)]
    full_list = []
    for vlan in all_vlans:
        if "-" in vlan:
            temp = vlan.split("-")
            full_list = full_list + list(range(int(temp[0]), int(temp[1])+1))
        else:
            full_list.append(int(vlan))
    return full_list


def vlan_range_shortener(full_vlan_list):
    """
    Function for shortening list of allowed VLANs on trunk interface. Example: `[1,2,3,4,5]` -> `["1-5"]`. Reverse function is ``vlan_range_expander``.

    :param full_vlan_list: List of integers representing VLAN numbers.
    :return: List of strings.
    """
    # TODO: Make more reliable
    shortened_vlan_list = []
    # Initialize with first element
    temp_element = str(full_vlan_list[0])

    for i in range(1, len(full_vlan_list)-1):
        if (full_vlan_list[i-1] + 1 == full_vlan_list[i]) and (full_vlan_list[i] + 1 == full_vlan_list[i+1]):
            # Do nothing
            continue
        if full_vlan_list[i-1] + 1 == full_vlan_list[i] and (full_vlan_list[i] + 1 != full_vlan_list[i+1]):
            # Close temp element and write
            temp_element = temp_element + "-" + str(full_vlan_list[i])
            shortened_vlan_list.append(temp_element)
            temp_element = ""
            continue
        if full_vlan_list[i - 1] + 1 != full_vlan_list[i] and (full_vlan_list[i] + 1 == full_vlan_list[i + 1]):
            # Begin new temp element
            temp_element = str(full_vlan_list[i])
            continue
        if full_vlan_list[i - 1] + 1 != full_vlan_list[i] and (full_vlan_list[i] + 1 != full_vlan_list[i + 1]):
            if temp_element != "":
                shortened_vlan_list.append(temp_element)
                temp_element = ""
            shortened_vlan_list.append(str(full_vlan_list[i]))
            continue
    # Close with end element
    if full_vlan_list[-1] == full_vlan_list[-2] + 1:
        temp_element = temp_element + "-" + str(full_vlan_list[-1])
        shortened_vlan_list.append(temp_element)
        temp_element = ""
    else:
        shortened_vlan_list.append(str(full_vlan_list[-1]))
    return shortened_vlan_list


def int_name_convert(int_name, out_type=None):
    """
    Function for converting long interface names to short and vice versa. Example: `"GigabitEthernet0/12"` -> `"Gi0/12"` and `"Gi0/12"` -> `"GigabitEthernet0/12"`

    :param str int_name: Interface name
    :param str out_type: Desired form of interface name, either `"long"` or `"short"`. If None, return opposite form
    :return: Interface name
    """
    int_type, int_num = interface_split(int_name)
    short = ["Eth", "Et", "Se", "Fa", "Gi", "Te", "Po", "Tu"]
    long = ["Ethernet", "Ethernet", "Serial", "FastEthernet", "GigabitEthernet", "TenGigabitEthernet", "Port-channel", "Tunnel"]
    if out_type is None:
        # Return opposite version
        if int_type in short:
            return long[short.index(int_type)] + int_num
        elif int_type in long:
            return short[long.index(int_type)] + int_num
        else:
            # Error
            return int_name
    elif out_type == "long":
        if int_type in short:
            return long[short.index(int_type)] + int_num
        elif int_type in long:
            return int_name
        else:
            # Error
            return int_name
    elif out_type == "short":
        if int_type in short:
            return int_name
        elif int_type in long:
            return short[long.index(int_type)] + int_num
        else:
            # Error
            return int_name
    else:
        return int_name


def mac_addr_convert(mac_address=u""):
    """
    Function for providing single format for MAC addresses.

    :param str mac_address: MAC address to be converted.
    :return: MAC address in format `XX:XX:XX:XX:XX:XX`.
    """
    try:
        mac = mac_address.replace(".", "")
        mac = [mac[i:i + 2].upper() for i in range(0, len(mac), 2)]
        mac = ":".join(mac)
        return mac
    except Exception as e:
        return mac_address


def update_dict(orig_dict, update_dict):
    """
    Function for updating dictionary values.

    :param dict orig_dict: Dictionary to be updated.
    :param dict update_dict: Dictionary to update from.
    :return: Updated dictionary.
    """
    for k, v in update_dict.items():
        if isinstance(v, collections.Mapping):
            orig_dict[k] = update_dict(orig_dict.get(k, {}), v)
        else:
            orig_dict[k] = v
    return orig_dict


def write_output(path, filename, data, logger=None):
    extension = ""
    data_type = type(data)
    if data_type is str:
        extension = ".txt"
    elif data_type in [dict, list]:
        extension = ".json"
    try:
        output_path = pathlib.Path(OUTPUT_PATH).joinpath(path)
        output_path.mkdir(parents=True, exist_ok=True)
        output_path = output_path.joinpath("{}{}".format(filename, extension))
        with output_path.open(mode="w") as f:
            if data_type in [dict, list]:
                json.dump(obj=data, fp=f, indent=2)
            else:
                f.write(str(data))
    except PermissionError:
        if logger:
            logger.error(msg="Could not write discovery results to file ('{}'). Reason: Permission Denied.".format(output_path))
        else:
            pass
    except Exception:
        if logger:
            logger.error(msg="Could not write discovery results to file ('{}'). Reason: Unhandled Exception: {}.".format(output_path, repr(e)))
        else:
            pass


def check_path(path, create_missing=True):
    """
    Function for checking path availability, returns `path` if specified folder exists, ``False`` otherwise. Can also create missing folders. Used for handling
    absolute and relative paths.

    :param str path: Path of the folder.
    :param bool create_missing: Whether or not to create missing folders.
    :return: Bool
    """
    if os.path.isabs(path):
        if not os.path.exists(path):
            if create_missing:
                os.makedirs(path)
                path = os.path.abspath(path)
                return path
            else:
                return False
        else:
            return os.path.abspath(path)
    else:
        # Prepend ROOT_DIR for relative paths
        path = os.path.abspath(os.path.join(ROOT_DIR, path))
        if not os.path.exists(path):
            if create_missing:
                os.makedirs(path)
                return path
            else:
                return False
        else:
            return path
