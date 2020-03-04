from netmiko import ConnectHandler
from netmiko.ssh_exception import *
import json
from nuaal.utils import get_logger, check_path, write_output
from nuaal.utils import Filter
from nuaal.definitions import DATA_PATH, OUTPUT_PATH
import timeit
import os

class CliBaseConnection(object):
    """
    This class represents the base object, from which other (vendor specific classes) inherit.
    This class is basically a wrapper class around Kirk Byers' excellent library, netmiko.
    Even though the netmiko library already provides pretty straightforward and easy way to access network devices,
    the CliBaseConnection tries to handle multiple events which can arise, such as:

    - Device is unreachable
    - Fallback to Telnet if SSH is not supported by device (and vice-versa)
    - Handles errors in outputs

    Apart from the 'send command, receive output'  this class also performs the parsing and storing outputs.
    """
    def __init__(
            self, ip=None, username=None, password=None,
            parser=None, secret=None, enable=False, store_outputs=False,
            DEBUG=False, verbosity=3, netmiko_params={}
    ):
        """

        :param ip: (str) IP address or FQDN of the device you're trying to connect to
        :param username: (str) Username used for login to device
        :param password: (str) Password used for login to device
        :param parser: (ParserModule) Instance of ParserModule class which will be used for parsing of text outputs.
        By default, new instance of ParserModule is created.
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
        self.netmiko_params = netmiko_params if isinstance(netmiko_params, dict) else {}
        self.provider = None
        self._get_provider()
        self.store_outputs = store_outputs
        self.enabled = False
        self.is_alive = False
        self.config = False
        self.prompt_end = [">", "#"] # The first item is for 'not-enabled mode', the second is for 'Privileged EXEC Mode'
        self.logger = get_logger(name="Connection-{}".format(self.ip), DEBUG=DEBUG, verbosity=verbosity)
        self.parser = parser
        self.connected = False
        self.failures = []
        self.outputs = {}
        self.data = {"ipAddress": self.ip}
        self.device = None

    def __enter__(self):
        """
        Enables usage of Python's Context Manager, using ``with`` statement.

        :return: Instance of the ``self`` object.
        """
        self._connect()
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        """
        This function is used when exiting Python's Context Manager.

        :return: ``None``
        """
        try:
            self.save_output(filename=self.data["hostname"], data=self.data)
        except KeyError:
            self.logger.error(msg="Could not store data of device {}. Reason: Could not retrieve any data".format(self.ip))
        except Exception as e:
            self.logger.error(msg="Could not store data of device {}. Reason: Unhandled Exception: {}".format(self.ip, repr(e)))
        finally:
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
            device = ConnectHandler(**self.provider, **self.netmiko_params)
        except TimeoutError:
            self.logger.error(msg="Could not connect to '{}' using '{}'. Reason: TimeOut.".format(self.ip, self.telnet_method))
            self.failures.append("telnet_connection_timeout")
        except ConnectionRefusedError:
            self.failures.append("telnet_connection_refused")
            self.logger.error(msg="Could not connect to '{}' using '{}'. Reason: Connection Refused.".format(self.ip, self.telnet_method))
        # TODO: Check fix in netmiko
        except AttributeError("module 'serial' has no attribute 'EIGHTBITS'", ):
            pass
        except Exception as e:
            print(repr(e))
            self.failures.append("telnet_unknown")
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
            device = ConnectHandler(**self.provider, **self.netmiko_params)
        except NetMikoTimeoutException:
            self.failures.append("ssh_connection_timeout")
            self.logger.error(msg="Could not connect to '{}' using '{}'. Reason: Timeout.".format(self.ip, self.ssh_method))
        except NetMikoAuthenticationException:
            self.failures.append("ssh_auth_fail")
            self.logger.error(msg="Could not connect to '{}' using '{}'. Reason: Authentication Failed.".format(self.ip, self.ssh_method))
        # TODO: Check fix in netmiko
        except AttributeError("module 'serial' has no attribute 'EIGHTBITS'",):
            pass
        except Exception as e:
            print(repr(e))
            self.failures.append("ssh_unknown")
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
        if self.device is not None:
            if self.device.is_alive():
                self.is_alive = True
                self.logger.debug(msg="Connection is already established.")
            else:
                try:
                    self.logger.debug(msg="Trying to re-establish connection to device.")
                    self.device.establish_connection()
                    self.device.session_preparation()
                    self._check_enable_level(self.device)
                except Exception as e:
                    self.logger.critical(msg="Failed to reconnect do device.")
        else:
            self.is_alive = False
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
            if device.is_alive():
                self.is_alive = True
            else:
                self.logger.critical(msg="Connection is not alive.")
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
                self.is_alive = False
                self.logger.info(msg="Successfully disconnected from device {}".format(self.ip))
            else:
                self.is_alive = True
                self.logger.error(msg="Failed to disconnect from device {}".format(self.ip))
        else:
            self.logger.info(msg="Device {} is not connected.".format(self.ip))

    def _send_command(self, command, expect_string=None):
        """

        :param str command: Command to send to device
        :return: Plaintext output of command from device
        """
        if (not self.device) or (not self.is_alive):
            self.logger.error(msg="Device {} is not connected, cannot send command.".format(self.ip))
            return None
        self.logger.debug(msg="Sending command '{}' to device {} ({})".format(command, self.data["hostname"], self.ip))
        output = None

        try:
            output = self.device.send_command(command_string=command, expect_string=expect_string)
        except AttributeError:
            self.logger.critical(msg="Connection to device {} has not been initialized.".format(self.ip))
        except Exception as e:
            self.logger.error(msg="Unhandled exception occurred when trying to send command. Exception: {}".format(repr(e)))
        finally:
            if output and self.store_outputs:
                self.save_output(filename=command, data=output)
            return output

    def _send_commands(self, commands):
        """
        Sends multiple commands to device.

        :param list commands: List of commands to run
        :return: Dictionary with key=command, value=output_of_the_command
        """
        output = {}
        for command in commands:
            output[command] = self._send_command(command)
        return output

    def _command_handler(self, commands=None, action=None, out_filter=None, return_raw=False):
        """
        This function tries to send multiple 'types' of given command and waits for correct output.
        This should solve the problem with different command syntax, such as 'show mac address-table' vs
        'show mac-address-table' on different versions of Cisco IOS.
        When correct output is returned, it is then parsed and the result is returned.

        :param str action: Action to perform - has to be key of self.command_mappings
        :param list commands: List of command string to try, such as ['show mac-address-table', 'show mac address-table']
        :param out_filter: Instance of Filter class
        :param bool return_raw: If set to `True`, raw output will be returned.
        :return: JSON representation of command output
        """
        start_time = timeit.default_timer()
        if commands is None:
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
                self.logger.error(msg="Device {}: Ambiguous command: '{}'".format(self.ip, command))
            elif command_output == "":
                self.logger.error(msg="Device {} returned empty output for command '{}'".format(self.ip, command))
            else:
                self.logger.debug(msg="Device {} returned output for command '{}'".format(self.ip, command))
                used_command = command
                break
        if self.store_outputs and command_output != "":
            self.save_output(filename=used_command, data=command_output)
        if command_output == "" or command_output is None:
            self.logger.error(msg="Device {} did not return output for any of the commands: {}".format(self.ip, commands))
            if return_raw:
                return ""
            else:
                return []
        if return_raw:
            return command_output
        else:
            # Try parsing the output
            try:
                parsed_output = self.parser.autoparse(command=commands[0], text=command_output)
                if isinstance(out_filter, Filter):
                    parsed_output = out_filter.universal_cleanup(data=parsed_output)
                if action is not None:
                    self.data[action[4:]] = parsed_output
            except Exception as e:
                print(repr(e))
                self.logger.error(msg="Device {}: Failed to parse output of command '{}'".format(self.ip, used_command))
            finally:
                self.logger.debug(msg="Processing of action {} took {} seconds.".format(action, timeit.default_timer()-start_time))
                return parsed_output

    def store_raw_output(self, command, raw_output, ext="txt"):
        """
        This function is used for storing the plaintext output of the commands called on the device in separate files. Used mainly for debugging and
        development purposes. This function is only called if the `store_outputs` parameter is set to `True`.

        :param str command: Command string executed on the device.
        :param str raw_output: Plaintext output of the command.
        :param str ext: Extension of the file, ".txt" by default.
        :return: ``None``
        """
        folder_name = str(self.ip)
        if "hostname" in self.data.keys():
            folder_name = "{}_{}".format(self.ip, self.data["hostname"])
        write_output(path=folder_name, filename=command.replace(" ", "_"), data=raw_output, logger=self.logger)
        """
        path = os.path.join(OUTPUT_PATH, self.ip)
        path = check_path(path)
        if path:
            with open(os.path.join(path, "{}.{}".format(command, ext)), mode="w+") as f:
                f.write(raw_output)
        """

    def save_output(self, filename, data):
        folder_name = str(self.ip)
        if "hostname" in self.data.keys():
            folder_name = "{}_{}".format(self.ip, self.data["hostname"])
        write_output(path=folder_name, filename=filename.replace(" ", "_"), data=data, logger=self.logger)


    def check_connection(self):
        """
        This function can be used to check state of the connection. Returns `True` if the connection is active and `False` if it isn't.

        :return: Bool value representing the connection state.
        """
        if self.device is not None:
            if self.device.is_alive():
                self.is_alive = True
                return True
            else:
                self.logger.error(msg="Connection is prepared, but not established.")
                self.is_alive = False
                return False
        else:
            self.logger.error(msg="Connection has not been initialized.")
            self.is_alive = False
            return False

    def config_mode(self):
        if self.check_connection():
            if self.device.check_config_mode():
                self.logger.debug(msg="Configuration mode is already enabled.")
                return True
            else:
                self.device.config_mode()
                if self.device.check_config_mode():
                    self.logger.info(msg="Configuration mode has been enabled.")
                    return True
                else:
                    self.logger.error(msg="Failed to enter configuration mode.")
                    return False
        else:
            self.logger.error(msg="Could not enter device configuration mode. Reason: Connection is not established.")
            return False



    #####################
    ### GET Functions ###
    #####################

    def get_vlans(self):
        """
        This function returns JSON representation of all VLANs enabled on the device, together with list of assigned interfaces. In Cisco terms, this represents
        the `show vlan brief` command.

        :return: List of dictionaries.
        """
        return self._command_handler(action="get_vlans")

    def get_inventory(self):
        """
        This function return JSON representation of all installed modules and HW parts of the device. In Cisco terms, this represents the command `show inventory`.

        :return: List of dictionaries.
        """
        return self._command_handler(action="get_inventory")

    def get_interfaces(self):
        """
        This function returns JSON representation of all physical and virtual interfaces of the device, containing all available info about each interface.
        In Cisco terms, this represents usage of command `show interfaces`.

        :return: List of dictionaries.
        """
        return self._command_handler(action="get_interfaces")

    def get_portchannels(self):
        """
        This function returns JSON representation of all logical bind interfaces (etherchannels, portchannels). In Cisco terms, this represents the
        `show etherchannel summary` command.

        :return: List of dictionaries.
        """
        return self._command_handler(action="get_portchannels")

    def get_license(self):

        """
        This function return JSON representation of licenses activated or installed on the device. In Cisco terms, this represents the `show license` command.

        :return: List of dictionaries.
        """
        return self._command_handler(action="get_license")

    def get_version(self):
        """
        Returns JSON representation of basic device information, such as vendor, device platform, software version etc. In Cisco terms, this represents the
        command `show version`.

        :return: List of dictionaries.
        """
        return self._command_handler(action="get_version")

    def get_mac_address_table(self):
        """
        Returns content of device MAC address table in JSON format. In Cisco terms, this represents the command `show mac address-table`.

        :return: List of dictionaries.
        """
        return self._command_handler(action="get_mac_address_table")

    def get_arp(self):
        """
        Returns content of device ARP table in JSON format. In Cisco terms, this represents the command `show ip arp`.

        :return: List of dictionaries.
        """
        return self._command_handler(action="get_arp")

    def __str__(self):
        return "[Connection -> {}]".format(self.ip)

    def __repr__(self):
        return "[Connection -> {}]".format(self.ip)