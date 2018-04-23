import logging
import sys
import os
import re
import collections
from nuaal.definitions import LOG_PATH, ROOT_DIR


def get_logger(name, DEBUG=False, handle=["stderr"]):
    logfile_path = os.path.join(check_path(LOG_PATH), "log.txt")
    formatter = logging.Formatter("[%(asctime)s] : %(name)s - %(levelname)s - %(message)s")
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
        if DEBUG:
            handler.setLevel(logging.DEBUG)
        else:
            handler.setLevel(logging.WARNING)

    root = logging.getLogger(name)
    root.setLevel(logging.DEBUG)
    root.propagate = 0
    root.addHandler(file_handler)
    for handler in handlers:
        root.addHandler(handler)

    return root

def interface_split(interface):
    # TODO: Make more reliable
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
    if isinstance(all_vlans, list):
        pass
    elif isinstance(all_vlans, str):
        all_vlans = all_vlans.split(",")
    full_list = []
    for vlan in all_vlans:
        if "-" in vlan:
            temp = vlan.split("-")
            full_list = full_list + list(range(int(temp[0]), int(temp[1])+1))
        else:
            full_list.append(int(vlan))
    return full_list


def vlan_range_shortener(full_vlan_list):
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


def int_name_convert(int_name):
    int_type, int_num = interface_split(int_name)
    short = ["Eth", "Se", "Fa", "Gi", "Te", "Po"]
    long = ["Ethernet", "Serial", "FastEthernet", "GigabitEthernet", "TenGigabitEthernet", "Port-channel"]
    new_int = ""
    if int_type in short:
        new_int = long[short.index(int_type)] + int_num
    elif int_type in long:
        new_int = short[long.index(int_type)] + int_num
    else:
        new_int = int_type + int_num
    return new_int

def update_dict(orig_dict, update_dict):
    for k, v in update_dict.items():
        if isinstance(v, collections.Mapping):
            orig_dict[k] = update_dict(orig_dict.get(k, {}), v)
        else:
            orig_dict[k] = v
    return orig_dict

def check_path(path, create_missing=True):
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
