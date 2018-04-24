from netmiko import ConnectHandler
from netmiko.ssh_exception import *
import json
from nuaal.utils import get_logger, check_path
from nuaal.utils import Filter
from nuaal.definitions import DATA_PATH
import timeit

class CliBaseConnection(object):
    """
    This class represents the base object, from which other (vendor specific classes) inherit. This class is basically a wrapper class around Kirk Byers' excellent library, netmiko. Even though the netmiko library already provides pretty straightforward and easy way to access network devices, the CliBaseConnection tries to handle multiple events which can arise, such as:

    - Device is unreachable
    - Fallback to Telnet if SSH is not supported by device (and vice-versa)
    - Handles errors in outputs

    Apart from the 'send command, receive output'  this class also performs the parsing and storing outputs.
    """
    def __init__(self, ip=None, username=None, password=None, parser=None, secret=None, enable=False, store_outputs=False, DEBUG=False):
        """

        :param ip: (str) IP address or FQDN of the device you're trying to connect to
        :param username: (str) Username used for login to device
        :param password: (str) Password used for login to device
        :param parser: (ParserModule) Instance of ParserModule class which will be used for parsing of text outputs. By default, new instance of ParserModule is created.
        :param secret: (str) Enable secret for accessing Privileged EXEC Mode
        :param enable: (bool) Whether or not enable Privileged EXEC Mode on device
        :param store_outputs: (bool) Whether or not store text outputs of sent commands
        :param DEBUG: (bool) Enable debugging logging
        """
        self.ip = ip
        self.username = username
        self.password = password
        self.ssh_method = None
        self.telnet_method = None
        self.primary_method = None
        self.secondary_method = None
        self.secret = secret
        self.enable = enable
        self.provider = None
        self._get_provider()
        self.store_outputs = store_outputs
        self.enabled = None
        self.prompt_end = [">", "#"] # The first item is for 'not-enabled mode', the second is for 'Privileged EXEC Mode'
        self.logger = get_logger(name="Connection-{}".format(self.ip), DEBUG=DEBUG)
        self.parser = parser
        self.connected = False

        self.outputs = {}
        self.data = {"ipAddress": self.ip}
        self.device = None

    def __enter__(self):
        self._connect()
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.store_raw_output(self.data["hostname"], json.dumps(self.data, indent=2), ext="json")
        self.disconnect()

    def _get_provider(self):
        """
        Creates provider dictionary for Netmiko connection

        :return: ``None``
        """
        self.provider = {
            "ip": self.ip,
            "username": self.username,
            "password": self.password
        }
        if self.secret:
            self.provider["secret"] = self.secret

    def _connect_telnet(self):
        """
        This function tries to establish connection with device via Telnet

        :return: (``netmiko.ConnectHandler``) device
        """
        device = None
        self.provider["device_type"] = self.telnet_method
        self.logger.debug(msg="Trying to connect to device {} via Telnet...".format(self.ip))
        try:
            device = ConnectHandler(**self.provider)
        except TimeoutError:
            self.logger.error(msg="Could not connect to '{}' using '{}'. Reason: TimeOut.".format(self.ip, self.telnet_method))
        except ConnectionRefusedError:
            self.logger.error(msg="Could not connect to '{}' using '{}'. Reason: Connection Refused.".format(self.ip, self.telnet_method))
        except Exception as e:
            print(repr(e))
            self.logger.error(msg="Could not connect to '{}' using '{}'. Reason: Unknown.".format(self.ip, self.telnet_method))
        finally:
            if device:
                self.logger.info(msg="Connected to '{}' using '{}'.".format(self.ip, self.telnet_method))
            return device

    def _connect_ssh(self):
        """
        This function tries to establish connection with device via SSH

        :return: (``netmiko.ConnectHandler``) device
        """
        device = None
        self.logger.debug(msg="Trying to connect to device {} via SSH...".format(self.ip))
        self.provider["device_type"] = self.ssh_method
        try:
            device = ConnectHandler(**self.provider)
        except NetMikoTimeoutException:
            self.logger.error(msg="Could not connect to '{}' using '{}'. Reason: Timeout.".format(self.ip, self.ssh_method))
        except NetMikoAuthenticationException:
            self.logger.error(msg="Could not connect to '{}' using '{}'. Reason: Authentication Failed.".format(self.ip, self.ssh_method))
        except Exception as e:
            print(repr(e))
            self.logger.error(msg="Could not connect to '{}' using '{}'. Reason: Unknown.".format(self.ip, self.ssh_method))
        finally:
            if device:
                self.logger.info(msg="Connected to '{}' using '{}'.".format(self.ip, self.ssh_method))
            return device

    def _connect(self):
        """
        This function handles connection to device, if primary method fails, it will try to connect using secondary method.

        :return: ``None``
        """
        device = None

        if self.primary_method == self.ssh_method:
            device = self._connect_ssh()
        elif self.primary_method == self.telnet_method:
            device = self._connect_telnet()
        if not device:
            if self.secondary_method == self.telnet_method:
                device = self._connect_telnet()
            elif self.secondary_method == self.ssh_method:
                self._connect_ssh()

        if device is not None:
            self._check_enable_level(device)
        else:
            self.logger.error(msg="Could not connect to device '{}'".format(self.ip))

    def _check_enable_level(self, device):
        """
        This function is called at the end of ``self._connect()`` to ensure that the connection is actually alive
        and that the proper privilege level is set.

        :param device: (``Netmiko.ConnectHandler``) Instance of ``netmiko.ConnectHandler``. If the connection is working, this will be set as ``self.device``
        :return: ``None``
        """
        try:
            prompt = device.find_prompt()
            self.data["hostname"] = prompt[:-1]
            if prompt[-1] == self.prompt_end[0]:
                self.enabled = False
            if prompt[-1] == self.prompt_end[1]:
                self.enabled = True
            if self.enable and not self.enabled:
                device.enable()
                if device.find_prompt()[-1] == self.prompt_end[1]:
                    self.logger.debug(msg="Successfully enabled Privileged EXEC Mode on device '{}'".format(self.ip))
                    self.enabled = True
                else:
                    self.logger.error(msg="Failed to enable Privileged EXEC Mode on device '{}'".format(self.ip))
            if not self.enable and self.enabled:
                device.exit_enable_mode()
                if device.find_prompt()[-1] ==self.prompt_end[0]:
                    self.logger.debug(msg="Successfully disabled Privileged EXEC Mode on device '{}'".format(self.ip))
                    self.enabled = True
                else:
                    self.logger.error(msg="Failed to disable Privileged EXEC Mode on device '{}'".format(self.ip))
        except ValueError as e:
            self.logger.critical(msg="Could not enter enable mode: {}".format(repr(e)))
        except Exception as e:
            print(repr(e))
        finally:
            self.device = device

    def disconnect(self):
        """
        This function handles graceful disconnect from the device.

        :return: ``None``
        """
        if self.device is not None:
            self.device.disconnect()
            if not self.device.is_alive():
                self.logger.info(msg="Successfully disconnected from device {}".format(self.ip))
            else:
                self.logger.error(msg="Failed to disconnect from device {}".format(self.ip))
        else:
            self.logger.info(msg="Device {} is not connected.".format(self.ip))

    def _send_command(self, command):
        """

        :param command: (str) Command to send to device
        :return: (str) Output of command from device
        """
        if not self.device:
            self.logger.error(msg="Device {} is not connected, cannot send command.".format(self.ip))
            return None
        self.logger.debug(msg="Sending command '{}' to device {} ({})".format(command, self.data["hostname"], self.ip))
        output = ""
        try:
            output = self.device.send_command_expect(command)
        except AttributeError:
            self.logger.critical(msg="Connection to device {} has not been initialized.".format(self.ip))
        finally:
            return output

    def _send_commands(self, commands):
        output = {}
        for command in commands:
            output[command] = self._send_command(command)
        return output

    def _command_handler(self, action, filter=None):
        """
        This function tries to send multiple 'types' of given command and waits for correct output.
        This should solve the problem with different command syntax, such as 'show mac address-table' vs
        'show mac-address-table' on different versions of Cisco IOS.
        When correct output is returned, it is then parsed and the result is returned.

        :param commands: List of command string to try, such as ['show mac-address-table', 'show mac address-table']
        :return: JSON representation of command output
        """
        start_time = timeit.default_timer()
        commands = self.command_mappings[action]
        command_output = ""
        used_command = ""
        parsed_output = []
        for command in commands:
            command_output = self._send_command(command)
            if not command_output:
                self.logger.error(msg="Could not retrieve any output. Possibly non-active connection.")
                return []
            if "% Invalid input detected at '^' marker." in command_output:
                self.logger.error(msg="Device {} does not support command '{}'".format(self.ip, command))
            elif "% Ambiguous command:" in command_output:
                self.logger.error(msg="Device {self.ip}: Ambiguous command: '{command}'")
            elif command_output == "":
                self.logger.error(msg="Device {} returned empty output for command '{}'".format(self.ip, command))
            else:
                self.logger.debug(msg="Device {} returned output for command '{}'".format(self.ip, command))
                used_command = command
                break
        if self.store_outputs and command_output != "":
            self.store_raw_output(command=used_command, raw_output=command_output)
        if command_output == "":
            return []
        # Try parsing the output
        try:
            parsed_output = self.parser.autoparse(command=commands[0], text=command_output)
            if isinstance(filter, Filter):
                parsed_output = filter.universal_cleanup(data=parsed_output)
            self.data[action[4:]] = parsed_output
        except Exception as e:
            print(repr(e))
            self.logger.error(msg="Device {}: Failed to parse output of command '{}'".format(self.ip, used_command))
        finally:
            self.logger.debug(msg="Processing of action {} took {} seconds.".format(action, timeit.default_timer()-start_time))
            return parsed_output

    def store_raw_output(self, command, raw_output, ext="txt"):
        path = "{}/outputs/{}".format(DATA_PATH, self.ip)
        path = check_path(path)
        if path:
            with open("{}/{}.{}".format(path, command, ext), mode="w+") as f:
                f.write(raw_output)

    #####################
    ### GET Functions ###
    #####################

    def get_vlans(self):
        return self._command_handler(action="get_vlans")

    def get_inventory(self):
        return self._command_handler(action="get_inventory")

    def get_interfaces(self):
        return self._command_handler(action="get_interfaces")

    def get_portchannels(self):
        return self._command_handler(action="get_portchannels")

    def get_license(self):
        return self._command_handler(action="get_license")

    def get_version(self):
        return self._command_handler(action="get_version")

    def get_mac_address_table(self):
        return self._command_handler(action="get_mac_address_table")

    def get_arp(self):
        return self._command_handler(action="get_arp")

    def __str__(self):
        return "[Connection -> {self.ip}]".format(self.ip)

    def __repr__(self):
        return "[Connection -> {self.ip}]".format(self.ip)